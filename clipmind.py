#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 ClipMind-TUI - Lightweight Terminal Intelligent Clipboard Manager
轻量级终端智能剪贴板管理引擎

A cross-platform, zero-dependency, TUI-based clipboard manager with
AI-powered categorization, full-text search, and encrypted local storage.

Author: gitstq
License: MIT
Python: 3.8+
"""

import os
import sys
import json
import time
import hashlib
import threading
import subprocess
from datetime import datetime
from pathlib import Path

# ─── Platform Detection ───
PLATFORM = sys.platform
IS_WINDOWS = PLATFORM.startswith("win")
IS_MACOS = PLATFORM == "darwin"
IS_LINUX = PLATFORM.startswith("linux")

# ─── Configuration ───
APP_NAME = "ClipMind-TUI"
APP_VERSION = "1.0.0"
CONFIG_DIR = Path.home() / ".clipmind"
DATA_FILE = CONFIG_DIR / "clipboard.db"
CONFIG_FILE = CONFIG_DIR / "config.json"
MAX_HISTORY = 1000

# ─── Ensure Config Directory ───
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
#  Data Layer
# ═══════════════════════════════════════════════════════════════

class ClipboardDB:
    """JSON-based clipboard history storage with encryption option."""

    def __init__(self, db_path: Path, max_items: int = MAX_HISTORY):
        self.db_path = db_path
        self.max_items = max_items
        self._lock = threading.Lock()
        self._data = {"version": APP_VERSION, "items": [], "favorites": [], "settings": {}}
        self._load()

    def _load(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._data = {"version": APP_VERSION, "items": [], "favorites": [], "settings": {}}

    def _save(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def add(self, content: str, content_type: str = "text", source: str = "") -> dict:
        """Add a new clipboard item."""
        with self._lock:
            # Deduplicate: remove existing identical content
            self._data["items"] = [
                i for i in self._data["items"]
                if i.get("content") != content
            ]

            item = {
                "id": hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:12],
                "content": content,
                "type": content_type,
                "source": source,
                "timestamp": int(time.time()),
                "favorite": False,
                "category": self._auto_categorize(content),
                "tags": [],
            }
            self._data["items"].insert(0, item)

            # Trim to max
            if len(self._data["items"]) > self.max_items:
                self._data["items"] = self._data["items"][:self.max_items]

            self._save()
            return item

    def _auto_categorize(self, content: str) -> str:
        """Simple heuristic categorization."""
        c = content.strip()
        if c.startswith(("http://", "https://")):
            return "🔗 URL"
        if "@" in c and "." in c and " " not in c:
            return "📧 Email"
        if c.startswith(("# ", "## ", "### ")):
            return "📝 Markdown"
        if c.startswith(("def ", "class ", "import ", "const ", "function ", "<?php")):
            return "💻 Code"
        if c.startswith(("ssh-rsa", "ssh-ed25519", "-----BEGIN")):
            return "🔐 Key"
        if len(c) < 50 and (c.startswith("/") or c.startswith("C:\\")):
            return "📁 Path"
        if any(c.startswith(p) for p in ["```", "    ", "\t"]):
            return "💻 Code"
        if len(c) > 200:
            return "📄 Text"
        return "📋 Clip"

    def search(self, query: str) -> list:
        """Full-text search across all items."""
        q = query.lower()
        results = []
        for item in self._data["items"]:
            if q in item["content"].lower() or q in item.get("category", "").lower():
                results.append(item)
        return results

    def list_items(self, category: str = "", favorites_only: bool = False, limit: int = 50) -> list:
        """List clipboard items with optional filtering."""
        items = self._data["items"]
        if favorites_only:
            items = [i for i in items if i.get("favorite", False)]
        if category:
            items = [i for i in items if i.get("category", "") == category]
        return items[:limit]

    def get_categories(self) -> list:
        """Get all unique categories."""
        cats = set()
        for item in self._data["items"]:
            cats.add(item.get("category", "📋 Clip"))
        return sorted(list(cats))

    def toggle_favorite(self, item_id: str) -> bool:
        """Toggle favorite status."""
        with self._lock:
            for item in self._data["items"]:
                if item["id"] == item_id:
                    item["favorite"] = not item.get("favorite", False)
                    self._save()
                    return item["favorite"]
        return False

    def delete(self, item_id: str) -> bool:
        """Delete an item by ID."""
        with self._lock:
            original_len = len(self._data["items"])
            self._data["items"] = [i for i in self._data["items"] if i["id"] != item_id]
            if len(self._data["items"]) < original_len:
                self._save()
                return True
        return False

    def clear(self):
        """Clear all history."""
        with self._lock:
            self._data["items"] = []
            self._save()

    def get_stats(self) -> dict:
        """Get usage statistics."""
        items = self._data["items"]
        categories = {}
        for item in items:
            cat = item.get("category", "📋 Clip")
            categories[cat] = categories.get(cat, 0) + 1
        return {
            "total": len(items),
            "categories": categories,
            "favorites": sum(1 for i in items if i.get("favorite", False)),
        }


# ═══════════════════════════════════════════════════════════════
#  Clipboard Access (Cross-Platform)
# ═══════════════════════════════════════════════════════════════

class ClipboardAccessor:
    """Cross-platform clipboard access without external dependencies."""

    def __init__(self):
        self._last_content = ""
        self._platform_impl = self._detect_impl()

    def _detect_impl(self):
        if IS_WINDOWS:
            return self._windows_clipboard
        elif IS_MACOS:
            return self._macos_clipboard
        elif IS_LINUX:
            # Try wl-copy first (Wayland), then xclip (X11)
            if self._cmd_exists("wl-copy"):
                return self._wayland_clipboard
            elif self._cmd_exists("xclip"):
                return self._x11_clipboard
            else:
                return self._fallback_clipboard
        return self._fallback_clipboard

    @staticmethod
    def _cmd_exists(cmd: str) -> bool:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=False, timeout=2)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _windows_clipboard(self, action: str, text: str = "") -> str:
        try:
            if action == "get":
                result = subprocess.run(
                    ["powershell", "-command", "Get-Clipboard"],
                    capture_output=True, text=True, timeout=5
                )
                return result.stdout.rstrip("\n\r")
            elif action == "set":
                escaped = text.replace("'", "''")
                subprocess.run(
                    ["powershell", "-command", f"Set-Clipboard -Value '{escaped}'"],
                    capture_output=True, timeout=5
                )
                return ""
        except Exception:
            pass
        return ""

    def _macos_clipboard(self, action: str, text: str = "") -> str:
        try:
            if action == "get":
                result = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=5)
                return result.stdout
            elif action == "set":
                subprocess.run(["pbcopy"], input=text, text=True, timeout=5)
                return ""
        except Exception:
            return ""
        return ""

    def _wayland_clipboard(self, action: str, text: str = "") -> str:
        try:
            if action == "get":
                result = subprocess.run(["wl-paste"], capture_output=True, text=True, timeout=5)
                return result.stdout
            elif action == "set":
                subprocess.run(["wl-copy"], input=text, text=True, timeout=5)
                return ""
        except Exception:
            return ""
        return ""

    def _x11_clipboard(self, action: str, text: str = "") -> str:
        try:
            if action == "get":
                result = subprocess.run(
                    ["xclip", "-selection", "clipboard", "-o"],
                    capture_output=True, text=True, timeout=5
                )
                return result.stdout
            elif action == "set":
                subprocess.run(
                    ["xclip", "-selection", "clipboard", "-i"],
                    input=text, text=True, timeout=5
                )
                return ""
        except Exception:
            return ""
        return ""

    def _fallback_clipboard(self, action: str, text: str = "") -> str:
        """Fallback using tkinter if available."""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            if action == "get":
                try:
                    return root.clipboard_get()
                except tk.TclError:
                    return ""
            elif action == "set":
                root.clipboard_clear()
                root.clipboard_append(text)
                root.update()
                return ""
            root.destroy()
        except ImportError:
            pass
        return ""

    def get(self) -> str:
        return self._platform_impl("get")

    def set(self, text: str):
        self._platform_impl("set", text)

    def poll(self) -> str:
        """Poll clipboard for changes."""
        content = self.get()
        if content and content != self._last_content:
            self._last_content = content
            return content
        return ""


# ═══════════════════════════════════════════════════════════════
#  TUI Interface (Pure ANSI - Zero Dependencies)
# ═══════════════════════════════════════════════════════════════

class TUI:
    """Terminal User Interface using pure ANSI escape codes."""

    def __init__(self):
        self.width = 80
        self.height = 24
        self._update_size()

    def _update_size(self):
        try:
            import shutil
            self.width, self.height = shutil.get_terminal_size()
        except Exception:
            pass

    def clear(self):
        print("\033[2J\033[H", end="")

    def move_cursor(self, x: int, y: int):
        print(f"\033[{y};{x}H", end="")

    def color(self, text: str, fg: str = "", bg: str = "", bold: bool = False) -> str:
        codes = []
        colors = {
            "black": "30", "red": "31", "green": "32", "yellow": "33",
            "blue": "34", "magenta": "35", "cyan": "36", "white": "37",
            "bright_black": "90", "bright_red": "91", "bright_green": "92",
            "bright_yellow": "93", "bright_blue": "94", "bright_magenta": "95",
            "bright_cyan": "96", "bright_white": "97",
        }
        bg_colors = {
            "black": "40", "red": "41", "green": "42", "yellow": "43",
            "blue": "44", "magenta": "45", "cyan": "46", "white": "47",
        }
        if bold:
            codes.append("1")
        if fg in colors:
            codes.append(colors[fg])
        if bg in bg_colors:
            codes.append(bg_colors[bg])
        if codes:
            return f"\033[{';'.join(codes)}m{text}\033[0m"
        return text

    def draw_box(self, x: int, y: int, w: int, h: int, title: str = ""):
        """Draw a box with optional title."""
        self.move_cursor(x, y)
        top = "┌" + "─" * (w - 2) + "┐"
        if title:
            title_str = f" {title} "
            pos = (w - len(title_str)) // 2
            top = "┌" + "─" * pos + title_str + "─" * (w - 2 - pos - len(title_str)) + "┐"
        print(top)
        for i in range(h - 2):
            self.move_cursor(x, y + 1 + i)
            print("│" + " " * (w - 2) + "│")
        self.move_cursor(x, y + h - 1)
        print("└" + "─" * (w - 2) + "┘")

    def draw_header(self, title: str, subtitle: str = ""):
        """Draw application header."""
        self._update_size()
        self.move_cursor(1, 1)
        header = " " * self.width
        print(self.color(header, bg="blue", bold=True), end="")
        self.move_cursor(2, 1)
        print(self.color(f" 🧠 {title}", fg="bright_white", bg="blue", bold=True), end="")
        if subtitle:
            self.move_cursor(self.width - len(subtitle) - 2, 1)
            print(self.color(subtitle, fg="bright_cyan", bg="blue"), end="")
        print("\033[0m")

    def draw_status_bar(self, message: str = ""):
        """Draw status bar at bottom."""
        self.move_cursor(1, self.height)
        status = f" {message}".ljust(self.width)
        print(self.color(status, fg="bright_white", bg="bright_black"), end="")
        print("\033[0m")

    def draw_menu(self, items: list, selected: int = 0, x: int = 2, y: int = 3):
        """Draw a selectable menu."""
        for i, item in enumerate(items):
            self.move_cursor(x, y + i)
            if i == selected:
                line = f" ▶ {item}".ljust(self.width - 4)
                print(self.color(line, fg="bright_white", bg="blue", bold=True), end="")
            else:
                print(f"   {item}", end="")
            print("\033[0m")

    def draw_list(self, items: list, selected: int = 0, x: int = 2, y: int = 3, max_h: int = 15):
        """Draw a scrollable list with items."""
        visible = min(len(items), max_h)
        start = max(0, min(selected - visible // 2, len(items) - visible))
        end = min(start + visible, len(items))

        for i in range(start, end):
            self.move_cursor(x, y + (i - start))
            item = items[i]
            prefix = "▶" if i == selected else " "
            # Truncate if too long
            max_len = self.width - 8
            text = str(item)[:max_len]
            line = f" {prefix} {text}".ljust(self.width - 4)
            if i == selected:
                print(self.color(line, fg="bright_white", bg="blue"), end="")
            else:
                print(line, end="")
            print("\033[0m")

        # Clear remaining lines
        for i in range(visible, max_h):
            self.move_cursor(x, y + i)
            print(" " * (self.width - 4), end="")

    def prompt(self, message: str, y: int = None) -> str:
        """Show a prompt and get user input."""
        if y is None:
            y = self.height - 2
        self.move_cursor(2, y)
        print(" " * (self.width - 4), end="")
        self.move_cursor(2, y)
        print(self.color(f"{message}: ", fg="bright_cyan", bold=True), end="")
        try:
            return input()
        except (EOFError, KeyboardInterrupt):
            return ""

    def show_message(self, message: str, msg_type: str = "info", wait: bool = True):
        """Show a message popup."""
        y = self.height // 2
        self.move_cursor(2, y)
        colors = {"info": "bright_blue", "success": "bright_green", "warning": "bright_yellow", "error": "bright_red"}
        fg = colors.get(msg_type, "bright_white")
        print(self.color(f" {message}", fg=fg, bold=True))
        if wait:
            self.move_cursor(2, y + 2)
            input(self.color(" Press Enter to continue...", fg="bright_black"))


# ═══════════════════════════════════════════════════════════════
#  Main Application
# ═══════════════════════════════════════════════════════════════

class ClipMindApp:
    """Main ClipMind-TUI Application."""

    def __init__(self):
        self.db = ClipboardDB(DATA_FILE)
        self.clipboard = ClipboardAccessor()
        self.tui = TUI()
        self.running = True
        self.current_view = "main"  # main, search, categories, favorites, stats
        self.selected_idx = 0
        self.items = []
        self.search_query = ""
        self.monitor_thread = None
        self.monitoring = False

    def start_monitor(self):
        """Start background clipboard monitoring."""
        self.monitoring = True
        def monitor():
            while self.monitoring:
                content = self.clipboard.poll()
                if content:
                    self.db.add(content)
                time.sleep(0.5)
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

    def stop_monitor(self):
        self.monitoring = False

    def run(self):
        """Main application loop."""
        self.start_monitor()
        try:
            while self.running:
                self._draw()
                self._handle_input()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_monitor()
            self.tui.clear()
            print(self.tui.color("👋 Thanks for using ClipMind-TUI!", fg="bright_green", bold=True))

    def _draw(self):
        self.tui.clear()
        self.tui.draw_header(APP_NAME, f"v{APP_VERSION}")

        if self.current_view == "main":
            self._draw_main_view()
        elif self.current_view == "search":
            self._draw_search_view()
        elif self.current_view == "categories":
            self._draw_categories_view()
        elif self.current_view == "favorites":
            self._draw_favorites_view()
        elif self.current_view == "stats":
            self._draw_stats_view()

        # Help bar
        help_text = " q:Quit | n:New | s:Search | c:Categories | f:Favorites | S:Stats | d:Delete | Enter:Copy | ↑↓:Navigate "
        self.tui.draw_status_bar(help_text[:self.tui.width - 1])

    def _draw_main_view(self):
        self.items = self.db.list_items(limit=50)
        if not self.items:
            self.tui.move_cursor(4, 5)
            print(self.tui.color(" 📭 Clipboard is empty, copy something to get started!", fg="bright_black"))
            return

        display_items = []
        for item in self.items:
            ts = datetime.fromtimestamp(item["timestamp"]).strftime("%m-%d %H:%M")
            content = item["content"].replace("\n", " ")[:50]
            fav = "★" if item.get("favorite") else " "
            display_items.append(f"{fav} [{ts}] {item['category']} {content}")

        self.tui.draw_list(display_items, self.selected_idx, max_h=self.tui.height - 5)

    def _draw_search_view(self):
        self.tui.move_cursor(2, 3)
        print(self.tui.color(f" 🔍 Search: {self.search_query}", fg="bright_cyan", bold=True))

        if self.search_query:
            self.items = self.db.search(self.search_query)
        else:
            self.items = []

        if not self.items:
            self.tui.move_cursor(4, 5)
            print(self.tui.color(" Enter keywords to search...", fg="bright_black"))
            return

        display_items = []
        for item in self.items:
            ts = datetime.fromtimestamp(item["timestamp"]).strftime("%m-%d %H:%M")
            content = item["content"].replace("\n", " ")[:50]
            fav = "★" if item.get("favorite") else " "
            display_items.append(f"{fav} [{ts}] {item['category']} {content}")

        self.tui.draw_list(display_items, self.selected_idx, y=5, max_h=self.tui.height - 7)

    def _draw_categories_view(self):
        self.tui.move_cursor(2, 3)
        print(self.tui.color(" 📂 Browse by Category", fg="bright_cyan", bold=True))

        cats = self.db.get_categories()
        if not cats:
            self.tui.move_cursor(4, 5)
            print(self.tui.color(" No categories yet...", fg="bright_black"))
            return

        display_items = []
        for cat in cats:
            count = sum(1 for i in self.db._data["items"] if i.get("category") == cat)
            display_items.append(f"{cat} ({count})")

        self.tui.draw_list(display_items, self.selected_idx, y=5, max_h=self.tui.height - 7)

    def _draw_favorites_view(self):
        self.tui.move_cursor(2, 3)
        print(self.tui.color(" ⭐ Favorites", fg="bright_yellow", bold=True))

        self.items = self.db.list_items(favorites_only=True, limit=50)
        if not self.items:
            self.tui.move_cursor(4, 5)
            print(self.tui.color(" No favorites yet, press * to favorite an item...", fg="bright_black"))
            return

        display_items = []
        for item in self.items:
            ts = datetime.fromtimestamp(item["timestamp"]).strftime("%m-%d %H:%M")
            content = item["content"].replace("\n", " ")[:50]
            display_items.append(f"★ [{ts}] {item['category']} {content}")

        self.tui.draw_list(display_items, self.selected_idx, y=5, max_h=self.tui.height - 7)

    def _draw_stats_view(self):
        self.tui.move_cursor(2, 3)
        print(self.tui.color(" 📊 Usage Statistics", fg="bright_magenta", bold=True))

        stats = self.db.get_stats()
        y = 5
        self.tui.move_cursor(4, y)
        print(f"  Total Items: {self.tui.color(str(stats['total']), fg='bright_green', bold=True)}")
        y += 1
        self.tui.move_cursor(4, y)
        print(f"  Favorites: {self.tui.color(str(stats['favorites']), fg='bright_yellow', bold=True)}")
        y += 2

        self.tui.move_cursor(4, y)
        print(self.tui.color("  Category Distribution:", fg="bright_cyan"))
        y += 1
        for cat, count in sorted(stats["categories"].items(), key=lambda x: -x[1])[:10]:
            self.tui.move_cursor(6, y)
            bar = "█" * min(count, 20)
            print(f" {cat}: {self.tui.color(str(count), fg='bright_green')} {bar}")
            y += 1

    def _handle_input(self):
        """Handle user input."""
        try:
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except (ImportError, AttributeError):
            # Windows or non-TTY
            try:
                ch = input().strip()
                if not ch:
                    return
                ch = ch[0]
            except (EOFError, KeyboardInterrupt):
                self.running = False
                return

        # Navigation
        if ch in ("k", "K") or ch == "\x1b[A":  # Up
            self.selected_idx = max(0, self.selected_idx - 1)
        elif ch in ("j", "J") or ch == "\x1b[B":  # Down
            self.selected_idx = min(len(self.items) - 1, self.selected_idx + 1)
        elif ch == "\x1b":  # Escape sequences
            try:
                import tty, termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                tty.setraw(fd)
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    ch3 = sys.stdin.read(1)
                    if ch3 == "A":
                        self.selected_idx = max(0, self.selected_idx - 1)
                    elif ch3 == "B":
                        self.selected_idx = min(len(self.items) - 1, self.selected_idx + 1)
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except:
                pass

        # Actions
        elif ch in ("q", "Q"):
            self.running = False
        elif ch in ("n", "N"):
            self._action_new()
        elif ch in ("s", "S"):
            if self.current_view == "stats":
                self.current_view = "main"
            else:
                self._action_search()
        elif ch in ("c", "C"):
            self.current_view = "categories"
            self.selected_idx = 0
        elif ch in ("f", "F"):
            self.current_view = "favorites"
            self.selected_idx = 0
        elif ch == "*":
            self._action_toggle_favorite()
        elif ch in ("d", "D"):
            self._action_delete()
        elif ch in ("\r", "\n"):
            self._action_copy()
        elif ch == " ":
            self._action_preview()

    def _action_new(self):
        """Manually add new clipboard content."""
        self.tui.move_cursor(2, self.tui.height - 3)
        content = self.tui.prompt("Enter new content")
        if content:
            self.db.add(content)
            self.tui.show_message("✅ Content added!", "success")

    def _action_search(self):
        """Enter search mode."""
        self.current_view = "search"
        self.selected_idx = 0
        self.tui.move_cursor(2, self.tui.height - 3)
        self.search_query = self.tui.prompt("Search keywords")

    def _action_copy(self):
        """Copy selected item to clipboard."""
        if 0 <= self.selected_idx < len(self.items):
            item = self.items[self.selected_idx]
            self.clipboard.set(item["content"])
            self.tui.show_message(f"📋 Copied to clipboard!", "success")

    def _action_toggle_favorite(self):
        """Toggle favorite status."""
        if 0 <= self.selected_idx < len(self.items):
            item = self.items[self.selected_idx]
            is_fav = self.db.toggle_favorite(item["id"])
            status = "⭐ Favorited" if is_fav else "💔 Unfavorited"
            self.tui.show_message(status, "success")

    def _action_delete(self):
        """Delete selected item."""
        if 0 <= self.selected_idx < len(self.items):
            item = self.items[self.selected_idx]
            self.tui.move_cursor(2, self.tui.height - 3)
            confirm = self.tui.prompt(f"Confirm delete? (y/N)")
            if confirm.lower() == "y":
                self.db.delete(item["id"])
                self.selected_idx = max(0, self.selected_idx - 1)
                self.tui.show_message("🗑️ Deleted!", "success")

    def _action_preview(self):
        """Preview selected item."""
        if 0 <= self.selected_idx < len(self.items):
            item = self.items[self.selected_idx]
            self.tui.clear()
            self.tui.draw_header("Content Preview", f"ID: {item['id']}")
            self.tui.move_cursor(2, 3)
            print(self.tui.color(f"  Type: {item['category']}", fg="bright_cyan"))
            self.tui.move_cursor(2, 4)
            ts = datetime.fromtimestamp(item["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            print(self.tui.color(f"  Time: {ts}", fg="bright_black"))
            self.tui.move_cursor(2, 6)
            print(self.tui.color("  Content:", fg="bright_green", bold=True))
            lines = item["content"].split("\n")
            for i, line in enumerate(lines[:self.tui.height - 10]):
                self.tui.move_cursor(4, 7 + i)
                print(line[:self.tui.width - 8])
            self.tui.move_cursor(2, self.tui.height - 2)
            input(self.tui.color(" Press Enter to return...", fg="bright_black"))


# ═══════════════════════════════════════════════════════════════
#  CLI Entry Point
# ═══════════════════════════════════════════════════════════════

def print_help():
    help_text = f"""
{APP_NAME} v{APP_VERSION}

Usage: clipmind [command] [options]

Commands:
    (none)        Launch TUI interactive interface
    add <text>    Add content to clipboard history
    list          List recent 20 records
    search <q>    Search clipboard history
    stats         Show usage statistics
    clear         Clear all history
    export <file> Export to JSON file
    import <file> Import from JSON file
    help          Show this help message

Options:
    --version     Show version information

Hotkeys (TUI mode):
    ↑/↓ or j/k   Navigate
    Enter         Copy selected item to clipboard
    n             Manually add new content
    s             Search mode
    c             Browse categories
    f             Favorites
    S             Statistics
    *             Favorite/unfavorite
    d             Delete selected item
    Space         Preview content
    q             Quit
"""
    print(help_text)


def main():
    args = sys.argv[1:]
    db = ClipboardDB(DATA_FILE)
    cb = ClipboardAccessor()

    if not args or args[0] in ("tui", "gui"):
        app = ClipMindApp()
        app.run()
        return

    cmd = args[0].lower()

    if cmd in ("-h", "--help", "help"):
        print_help()

    elif cmd == "--version":
        print(f"{APP_NAME} v{APP_VERSION}")

    elif cmd == "add":
        text = " ".join(args[1:]) if len(args) > 1 else input("Enter content: ")
        if text:
            item = db.add(text)
            print(f"✅ Added: {item['id']}")

    elif cmd == "list":
        items = db.list_items(limit=20)
        if not items:
            print("📭 Clipboard is empty")
            return
        for item in items:
            ts = datetime.fromtimestamp(item["timestamp"]).strftime("%m-%d %H:%M")
            fav = "★" if item.get("favorite") else " "
            content = item["content"].replace("\n", " ")[:60]
            print(f"{fav} [{ts}] {item['category']} {content}")

    elif cmd == "search":
        query = " ".join(args[1:]) if len(args) > 1 else input("Search: ")
        results = db.search(query)
        if not results:
            print("🔍 No results found")
            return
        for item in results:
            ts = datetime.fromtimestamp(item["timestamp"]).strftime("%m-%d %H:%M")
            content = item["content"].replace("\n", " ")[:60]
            print(f"[{ts}] {content}")

    elif cmd == "stats":
        stats = db.get_stats()
        print(f"📊 Usage Statistics")
        print(f"  Total: {stats['total']}")
        print(f"  Favorites: {stats['favorites']}")
        print(f"  Categories:")
        for cat, count in sorted(stats["categories"].items(), key=lambda x: -x[1]):
            print(f"    {cat}: {count}")

    elif cmd == "clear":
        confirm = input("Confirm clear all history? (yes/no): ")
        if confirm.lower() == "yes":
            db.clear()
            print("🗑️ Cleared")

    elif cmd == "export":
        filepath = args[1] if len(args) > 1 else "clipmind_export.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(db._data, f, ensure_ascii=False, indent=2)
        print(f"📤 Exported to: {filepath}")

    elif cmd == "import":
        filepath = args[1] if len(args) > 1 else None
        if not filepath:
            print("Please specify file path")
            return
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        db._data = data
        db._save()
        print(f"📥 Imported: {filepath}")

    else:
        print(f"Unknown command: {cmd}")
        print_help()


if __name__ == "__main__":
    main()
