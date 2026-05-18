"""Animated toggle switch — drop-in QCheckBox replacement."""

from PyQt6.QtWidgets import QCheckBox, QSizePolicy
from PyQt6.QtCore    import Qt, QTimer, QSize, QPointF, QRectF
from PyQt6.QtGui     import (
    QPainter, QColor, QPen, QBrush, QFontMetrics, QPainterPath,
)


class ToggleSwitch(QCheckBox):
    """
    Pill-shaped animated toggle.  Fully API-compatible with QCheckBox:
    isChecked(), setChecked(), stateChanged, clicked.
    """

    # Layout constants
    TRACK_W = 46
    TRACK_H = 24
    KNOB_D  = 18
    GAP     = 10   # between track and label text

    # Colors
    _C_ON   = QColor("#0078d4")
    _C_OFF  = QColor("#555555")
    _C_KNOB = QColor("#ffffff")
    _C_HLT  = QColor("#1a8fe0")   # hovered ON
    _C_HLT_OFF = QColor("#686868") # hovered OFF

    # Animation speed (class-level, affects all instances)
    _ANIM_STEP = {
        "none":   1.0,    # instant
        "fast":   0.45,
        "normal": 0.28,
        "slow":   0.14,
    }
    _step_frac: float = 0.28   # current step fraction

    @classmethod
    def set_animation_speed(cls, speed: str):
        cls._step_frac = cls._ANIM_STEP.get(speed, 0.28)

    @classmethod
    def set_accent_color(cls, color: str):
        c = QColor(color)
        if not c.isValid():
            return
        cls._C_ON = c
        cls._C_HLT = QColor(
            min(255, c.red() + 24),
            min(255, c.green() + 24),
            min(255, c.blue() + 24),
        )

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(28)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,
                           QSizePolicy.Policy.Fixed)

        self._pos     = 1.0 if self.isChecked() else 0.0
        self._hovered = False

        self._timer = QTimer(self)
        self._timer.setInterval(14)          # ~70 fps
        self._timer.timeout.connect(self._step)
        self.stateChanged.connect(self._on_state)
        self.setMouseTracking(True)

    # ── Animation ─────────────────────────────────────────

    def _on_state(self, _):
        self._timer.start()

    def _step(self):
        target = 1.0 if self.isChecked() else 0.0
        diff   = target - self._pos
        if abs(diff) < 0.015 or self._step_frac >= 1.0:
            self._pos = target
            self._timer.stop()
        else:
            self._pos += diff * self._step_frac   # ease-out
        self.update()

    # ── Size ──────────────────────────────────────────────

    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self.font())
        tw = fm.horizontalAdvance(self.text())
        extra = self.GAP + tw if self.text() else 0
        return QSize(self.TRACK_W + extra + 4, 28)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    # ── Events ────────────────────────────────────────────

    def enterEvent(self, e):
        self._hovered = True
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hovered = False
        self.update()
        super().leaveEvent(e)

    def hitButton(self, pos) -> bool:
        return True    # whole widget toggles

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        t   = self._pos
        h   = self.height()
        ty  = (h - self.TRACK_H) // 2

        # ── Track color interpolation ─────────────────────
        if self._hovered:
            c_from = self._C_HLT_OFF
            c_to   = self._C_HLT
        else:
            c_from = self._C_OFF
            c_to   = self._C_ON

        def _lerp(a, b, x):
            return int(a * (1 - x) + b * x)

        track = QColor(
            _lerp(c_from.red(),   c_to.red(),   t),
            _lerp(c_from.green(), c_to.green(), t),
            _lerp(c_from.blue(),  c_to.blue(),  t),
        )

        # ── Track ─────────────────────────────────────────
        radius = self.TRACK_H / 2
        track_rect = QRectF(0, ty, self.TRACK_W, self.TRACK_H)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(track))
        p.drawRoundedRect(track_rect, radius, radius)

        # ── Knob ──────────────────────────────────────────
        travel = self.TRACK_W - self.KNOB_D - 4
        kx     = 2 + travel * t
        ky     = ty + (self.TRACK_H - self.KNOB_D) / 2

        # Shadow
        p.setBrush(QColor(0, 0, 0, 45))
        p.drawEllipse(QRectF(kx + 1, ky + 1.5, self.KNOB_D, self.KNOB_D))

        # Knob face
        p.setBrush(QBrush(self._C_KNOB))
        p.drawEllipse(QRectF(kx, ky, self.KNOB_D, self.KNOB_D))

        # ── Checkmark inside knob (when on) ───────────────
        if t > 0.5:
            alpha = int(min(1.0, (t - 0.5) * 2) * 220)
            pen   = QPen(QColor(track.red(), track.green(), track.blue(), alpha))
            pen.setWidth(2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            cx = kx + self.KNOB_D / 2
            cy = ky + self.KNOB_D / 2
            # Small tick: ✓
            p.drawLine(QPointF(cx - 4, cy),
                       QPointF(cx - 1, cy + 3))
            p.drawLine(QPointF(cx - 1, cy + 3),
                       QPointF(cx + 4, cy - 3))

        # ── Label text ────────────────────────────────────
        if self.text():
            alpha_txt = 255 if self.isEnabled() else 120
            txt_color = self.palette().text().color()
            txt_color.setAlpha(alpha_txt)
            p.setPen(txt_color)
            fm  = QFontMetrics(self.font())
            tx  = self.TRACK_W + self.GAP
            ty2 = (h + fm.ascent() - fm.descent()) // 2
            p.drawText(int(tx), ty2, self.text())

        p.end()
