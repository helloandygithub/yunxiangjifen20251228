#!/bin/bash
# 创建简单的SVG图标并转换为PNG

# 首页图标
cat > tab-home.svg << 'SVGEOF'
<svg width="81" height="81" xmlns="http://www.w3.org/2000/svg"><rect fill="#999" width="81" height="81" rx="8"/><path d="M40.5 25l-15 12v19h10V46h10v10h10V37z" fill="#fff"/></svg>
SVGEOF

cat > tab-home-active.svg << 'SVGEOF'
<svg width="81" height="81" xmlns="http://www.w3.org/2000/svg"><rect fill="#667EEA" width="81" height="81" rx="8"/><path d="M40.5 25l-15 12v19h10V46h10v10h10V37z" fill="#fff"/></svg>
SVGEOF

# 商城图标
cat > tab-mall.svg << 'SVGEOF'
<svg width="81" height="81" xmlns="http://www.w3.org/2000/svg"><rect fill="#999" width="81" height="81" rx="8"/><path d="M30 30h21v21H30z" fill="none" stroke="#fff" stroke-width="2"/><circle cx="35" cy="56" r="2" fill="#fff"/><circle cx="46" cy="56" r="2" fill="#fff"/><path d="M28 28l3 15h19l3-15" fill="none" stroke="#fff" stroke-width="2"/></svg>
SVGEOF

cat > tab-mall-active.svg << 'SVGEOF'
<svg width="81" height="81" xmlns="http://www.w3.org/2000/svg"><rect fill="#667EEA" width="81" height="81" rx="8"/><path d="M30 30h21v21H30z" fill="none" stroke="#fff" stroke-width="2"/><circle cx="35" cy="56" r="2" fill="#fff"/><circle cx="46" cy="56" r="2" fill="#fff"/><path d="M28 28l3 15h19l3-15" fill="none" stroke="#fff" stroke-width="2"/></svg>
SVGEOF

# 我的图标
cat > tab-user.svg << 'SVGEOF'
<svg width="81" height="81" xmlns="http://www.w3.org/2000/svg"><rect fill="#999" width="81" height="81" rx="8"/><circle cx="40.5" cy="35" r="8" fill="#fff"/><path d="M28 56c0-7 5.6-12 12.5-12s12.5 5 12.5 12" fill="none" stroke="#fff" stroke-width="2"/></svg>
SVGEOF

cat > tab-user-active.svg << 'SVGEOF'
<svg width="81" height="81" xmlns="http://www.w3.org/2000/svg"><rect fill="#667EEA" width="81" height="81" rx="8"/><circle cx="40.5" cy="35" r="8" fill="#fff"/><path d="M28 56c0-7 5.6-12 12.5-12s12.5 5 12.5 12" fill="none" stroke="#fff" stroke-width="2"/></svg>
SVGEOF

# 转换为PNG（如果有convert命令）
if command -v convert &> /dev/null; then
  for f in *.svg; do
    convert -background none "$f" "${f%.svg}.png"
  done
  rm *.svg
else
  # 如果没有ImageMagick，重命名svg为png（小程序也支持svg）
  for f in *.svg; do
    mv "$f" "${f%.svg}.png"
  done
fi

echo "TabBar icons created"
