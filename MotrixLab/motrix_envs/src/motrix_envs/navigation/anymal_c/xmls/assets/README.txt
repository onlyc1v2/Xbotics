复杂地形高度图放置说明
========================

请将 heightmap.png 放在以下任一位置：

1. 本目录（推荐）：将 heightmap.png 复制到当前 assets 目录下。
   路径示例：.../motrix_envs/navigation/anymal_c/xmls/assets/heightmap.png

2. 项目根目录：若您的 heightmap.png 在项目根目录的 assets 文件夹下，
   请修改 scene_rough_terrain.xml 中 hfield 的 file 属性为：
   file="../../../../../../assets/heightmap.png"
   （具体层级需根据您的目录结构调整）

高度图要求：灰度 PNG，像素值映射为地形高度（与 MuJoCo hfield 约定一致）。
