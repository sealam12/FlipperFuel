# overlay_display_fixed.py
# Requires PyQt5: pip install PyQt5

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import random

# -------------------------------------------------------------------
# Utilities for formatting (keeps same numeric formats as original)
# -------------------------------------------------------------------
def fmt_int(v, width=2):
    return f"{int(v):0{width}d}"

def fmt_float(v, width=6, precision=2):
    return f"{v:0{width}.{precision}f}"

# -------------------------------------------------------------------
# Panel widget (draws title + lines with precise metrics)
# -------------------------------------------------------------------
class Panel(QtWidgets.QWidget):
    def __init__(self, title_text, col_x, line_y, cols, lines, parent=None):
        super().__init__(parent)
        self.title_text = title_text
        self.col_x = col_x      # column index (characters) where panel begins
        self.line_y = line_y    # row index (lines) where panel begins
        self.cols = cols        # width in terminal columns (characters)
        self.lines = lines      # number of content lines
        self._padding_chars = 0  # left/right padding in characters
        self._title_padding_px = 6
        self._title_bar_extra_h = 6
        self._font = QtGui.QFont("JetBrains Mono")
        self._font.setStyleHint(QtGui.QFont.Monospace)
        self._font.setPointSize(11)
        self.setFont(self._font)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # content storage
        self.content = [""] * self.lines
        self.content_colors = [None] * self.lines

    def set_line(self, idx, text, color=None):
        if 0 <= idx < self.lines:
            # Ensure string lengths are not unexpectedly long (user code controls formatting)
            self.content[idx] = text
            self.content_colors[idx] = color
            self.update()

    def set_geometry_by_metrics(self, char_w, char_h, parent_padding_x=0, parent_padding_y=0):
        """
        Calculate widget geometry based on character width/height and assigned column/line position.
        This should be called when parent font metrics or parent size changes.
        """
        x = self.col_x * char_w + parent_padding_x
        y = self.line_y * char_h + parent_padding_y

        width = max((self.cols + (self._padding_chars * 2)) * char_w, 120)
        # title bar height plus content area
        title_bar_h = char_h + self._title_bar_extra_h
        height = title_bar_h + self.lines * char_h + 8
        self._title_bar_h = title_bar_h
        self._char_w = char_w
        self._char_h = char_h
        self.setGeometry(int(x), int(y), int(width), int(height))
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.TextAntialiasing | QtGui.QPainter.Antialiasing)

        # Colors
        bg_color = QtGui.QColor(60, 56, 54)
        text_color = QtGui.QColor(220, 220, 220)

        rect = self.rect()

        # Title bar
        title_rect = QtCore.QRect(0, 0, rect.width(), self._title_bar_h)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRect(title_rect)

        # Draw title centered (like the terminal header)
        painter.setPen(text_color)
        title_font = QtGui.QFont(self.font())
        title_font.setBold(True)
        painter.setFont(title_font)
        fm_title = QtGui.QFontMetrics(title_font)

        # text area for title centered with small horizontal padding
        title_text = self.title_text.strip()
        painter.drawText(title_rect.adjusted(self._title_padding_px, 0, -self._title_padding_px, 0),
                         QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter,
                         title_text)

        # Body (same bg)
        body_rect = QtCore.QRect(0, self._title_bar_h - 1, rect.width(), rect.height() - (self._title_bar_h - 1))
        painter.setBrush(bg_color)
        painter.drawRect(body_rect)

        # Draw lines
        painter.setFont(self.font())
        fm = QtGui.QFontMetrics(self.font())
        left_pad_px = self._padding_chars * self._char_w + 6

        # For each line, draw text vertically centered on its line's rectangle
        for i, text in enumerate(self.content):
            line_y = self._title_bar_h + i * self._char_h
            line_rect = QtCore.QRect(left_pad_px, line_y, rect.width() - left_pad_px - 6, self._char_h)
            color = self.content_colors[i] or text_color
            if isinstance(color, QtGui.QColor):
                painter.setPen(color)
            else:
                painter.setPen(text_color)
            # Align left and vertically center within the char height
            painter.drawText(line_rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, text)

        painter.end()

# -------------------------------------------------------------------
# Main overlay widget (frameless, transparent, draggable, resizable)
# -------------------------------------------------------------------
class OverlayDisplay(QtWidgets.QWidget):
    MIN_WIDTH = 320
    MIN_HEIGHT = 200

    def __init__(self, race_data, live_calculator, target_calculator):
        super().__init__(None, QtCore.Qt.Window)
        self.rd = race_data
        self.lc = live_calculator
        self.tc = target_calculator

        # Window flags for transparent, frameless, always on top
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        # Base font and metrics (we'll use this to compute char sizes)
        self.base_font = QtGui.QFont("JetBrains Mono")
        self.base_font.setStyleHint(QtGui.QFont.Monospace)
        self.base_font.setPointSize(11)
        self.setFont(self.base_font)

        # Internal dragging/resizing state
        self._drag_pos = None
        self._resizing = False
        self._resize_margin = 32  # px threshold for resize corner
        self._cursor_default = QtCore.Qt.ArrowCursor

        # Panels (positions use terminal-style columns/rows similar to original)
        # Columns mapping roughly: target_race at col 0, target_stint at col 26, live_min at col 0 spanning wide
        self.panel_target_race = Panel("   TARGET RACE        ", col_x=0, line_y=0, cols=26, lines=3, parent=self)
        self.panel_target_stint = Panel("  TARGET STINT      ", col_x=26, line_y=0, cols=26, lines=3, parent=self)
        self.panel_live_race = Panel("        LIVE RACE         ", col_x=0, line_y=6, cols=26, lines=4, parent=self)
        self.panel_live_stint = Panel("       LIVE STINT       ", col_x=26, line_y=6, cols=26, lines=4, parent=self)
        self.panel_live_minimum = Panel("                   LIVE MINIMUM                   ", col_x=0, line_y=13, cols=52, lines=3, parent=self)

        self.panels = [
            self.panel_target_race,
            self.panel_target_stint,
            self.panel_live_race,
            self.panel_live_stint,
            self.panel_live_minimum
        ]

        # Initial size and geometry mapping
        self.resize(760, 420)
        self._update_metrics_and_layout()

        # Timer to update every second similar to original script
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(50)
        self.update_display()

    def _update_metrics_and_layout(self):
        """Recompute char widths/heights from current font metrics and re-position panels."""
        fm = QtGui.QFontMetrics(self.font())
        # Use average char width (monospace so good)
        char_w = fm.horizontalAdvance('M')  # reliable monospace width
        char_h = fm.height()
        # small global padding; allows offset from window border
        parent_pad_x = 6
        parent_pad_y = 6
        # Apply to panels
        for p in self.panels:
            p.setFont(self.font())
            p.set_geometry_by_metrics(char_w, char_h, parent_pad_x, parent_pad_y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # On resize, recompute layout so panels are re-positioned (they won't auto-layout otherwise)
        self._update_metrics_and_layout()

    # ---- Mouse handling for drag & resize ----
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            r = self.rect()
            pos = event.pos()
            # If in bottom-right corner region => start resizing
            if pos.x() >= r.width() - self._resize_margin and pos.y() >= r.height() - self._resize_margin:
                self._resizing = True
                self._resize_anchor = event.globalPos()
                self._start_geo = self.geometry()
            else:
                # Start dragging
                self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        r = self.rect()
        # If resizing, compute new width/height
        if self._resizing:
            delta = event.globalPos() - self._resize_anchor
            new_w = max(self.MIN_WIDTH, self._start_geo.width() + delta.x())
            new_h = max(self.MIN_HEIGHT, self._start_geo.height() + delta.y())
            self.resize(new_w, new_h)
            event.accept()
            return

        if self._drag_pos is not None and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
            return

        # Otherwise update cursor if near bottom-right
        if pos.x() >= r.width() - self._resize_margin and pos.y() >= r.height() - self._resize_margin:
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        else:
            self.setCursor(self._cursor_default)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._resizing = False
        self.setCursor(self._cursor_default)
        event.accept()

    # Optional: draw a subtle outline for debugging (disabled by default)
    def paintEvent(self, event):
        # leave empty for transparent background (or draw debug border)
        pass

    # ---- Populate panels using your same logic from terminal code ----
    def update_display(self):
        try:
            # TARGET RACE
            self.panel_target_race.set_line(0, f"STINTS                {fmt_int(self.rd.targets.stint_target, 2)}")
            self.panel_target_race.set_line(1, f"LAPS                 {fmt_int(self.lc.total_race_laps(), 3)}")
            self.panel_target_race.set_line(2, f"FUEL              {fmt_float(self.lc.total_race_fuel(), 6, 2)}")

            # TARGET STINT
            self.panel_target_stint.set_line(0, f"LAP FUEL            {fmt_float(self.tc.lap_fuel_required(), 4, 2)}")
            self.panel_target_stint.set_line(1, f"LAPS               {fmt_float(self.tc.stint_laps_required(), 5, 2)}")
            self.panel_target_stint.set_line(2, f"TIME               {fmt_float(self.tc.stint_time_required(), 5, 2)}")

            # LIVE RACE color logic
            proj_stints = self.lc.projected_stints_total()
            proj_color = None
            if proj_stints > self.rd.targets.stint_target:
                proj_color = QtGui.QColor(200, 30, 30)
            elif proj_stints < self.rd.targets.stint_target:
                proj_color = QtGui.QColor(40, 150, 40)

            self.panel_live_race.set_line(0, f"FUEL R            {fmt_float(self.lc.remaining_race_fuel(), 6, 2)}")
            self.panel_live_race.set_line(1, f"LAPS R               {fmt_int(self.lc.remaining_race_laps(), 3)}")
            self.panel_live_race.set_line(2, f"STINTS PROJ           {fmt_int(self.lc.projected_stints_total(), 2)}", proj_color)
            self.panel_live_race.set_line(3, f"STINTS REMN           {fmt_int(self.lc.projected_stints_remaining(), 2)}", proj_color)

            # LIVE STINT color logic
            lf_color = None
            if self.rd.live_data.avg_lap_fuel > self.tc.lap_fuel_required():
                lf_color = QtGui.QColor(200, 160, 40)  # yellow
            if self.rd.live_data.avg_lap_fuel > self.lc.lap_fuel_required():
                lf_color = QtGui.QColor(200, 30, 30)   # red
            if self.rd.live_data.avg_lap_fuel < (self.lc.lap_fuel_required() * 0.96):
                lf_color = QtGui.QColor(40, 150, 40)   # green

            self.panel_live_stint.set_line(0, f"AVG FUEL            {fmt_float(self.rd.live_data.avg_lap_fuel, 4, 2)}", lf_color)
            self.panel_live_stint.set_line(1, f"FUEL R             {fmt_float(self.rd.live_data.fuel_remaining, 5, 2)}")
            self.panel_live_stint.set_line(2, f"LAPS R             {fmt_float(self.lc.current_stint_laps_remaining(), 5, 2)}")
            self.panel_live_stint.set_line(3, f"TIME R             {fmt_float(self.lc.current_stint_time_remaining(), 5, 2)}")

            # LIVE MINIMUM with highlights
            lf_color = QtGui.QColor(200, 160, 40) if (self.lc.lap_fuel_required() < self.tc.lap_fuel_required()) else None
            l_color = QtGui.QColor(200, 160, 40) if (self.lc.stint_laps_required() > self.tc.stint_laps_required()) else None
            t_color = QtGui.QColor(200, 160, 40) if (self.lc.stint_time_required() > self.tc.stint_time_required()) else None

            self.panel_live_minimum.set_line(0, f"LAP FUEL                                      {fmt_float(self.lc.lap_fuel_required(), 4, 2)}", lf_color)
            self.panel_live_minimum.set_line(1, f"LAPS                                         {fmt_float(self.lc.stint_laps_required(), 5, 2)}", l_color)
            self.panel_live_minimum.set_line(2, f"TIME                                         {fmt_float(self.lc.stint_time_required(), 5, 2)}", t_color)

        except Exception as e:
            # If anything goes wrong, print error to console but keep overlay running
            print("Error updating overlay:", e)
