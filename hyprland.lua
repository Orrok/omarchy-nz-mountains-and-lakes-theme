-- NZ - Mountains and Lakes.
--
-- The forest theme rounds its corners because nothing in a forest is square.
-- This one does the opposite on purpose: mountains and ice are angular, so the
-- corners stay nearly sharp and the shadow is tight and hard, like alpine light.
-- Blur stands in for the haze that hangs over a glacier lake, and unfocused
-- windows recede the way a distant range fades into that haze.
--
-- Note for anyone reading this from the repository: Omarchy discards a cloned
-- theme's .lua files, so everything below applies only when the theme is a
-- directory you wrote (or a symlink to your own working copy). The border
-- gradient lives in colors.toml instead, precisely so that it survives.
local active_border_color = { colors = { "rgba(4fc8e8ee)", "rgba(58a6f0ee)" }, angle = 45 }
local inactive_border_color = "rgba(1e3a5499)"

hl.config({
  general = {
    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  },

  decoration = {
    -- Rock and ice, not leaves. Just enough to avoid a hard pixel corner.
    rounding = 4,

    -- Distance haze: whatever you are not working in falls back a valley.
    dim_inactive = true,
    dim_strength = 0.18,

    -- Mist over cold water, on the bar and menus.
    blur = {
      enabled = true,
      size = 6,
      passes = 2,
      new_optimizations = true,
      ignore_opacity = true,
    },

    -- Hard high-altitude light casts a tight shadow, not a soft one.
    shadow = {
      enabled = true,
      range = 5,
      render_power = 4,
      color = "rgba(050b16cc)",
      color_inactive = "rgba(050b1666)",
    },
  },
})
