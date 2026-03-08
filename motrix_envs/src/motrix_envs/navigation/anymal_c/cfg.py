#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import os
from dataclasses import dataclass,field

from motrix_envs import registry
from motrix_envs.base import EnvCfg

model_file = os.path.dirname(__file__) + "/xmls/scene.xml"

@dataclass
class NoiseConfig:
    level: float = 1.0
    scale_joint_angle: float = 0.03
    scale_joint_vel: float = 1.5
    scale_gyro: float = 0.2
    scale_gravity: float = 0.05
    scale_linvel: float = 0.1

@dataclass
class ControlConfig:
    # stiffness[N*m/rad] 使用XML中kp参数，仅作记录
    # damping[N*m*s/rad] 使用XML中kv参数，仅作记录
    action_scale = 0.06  # 动作幅度
    # torque_limit[N*m] 使用XML forcerange参数

@dataclass
class InitState:
    # the initial position of the robot in the world frame
    pos = [0.0, 0.0, 0.5]  # Z轴高度与XML中base的初始高度一致
    
    # 位置随机化范围 [x_min, y_min, x_max, y_max]
    pos_randomization_range = [-10.0, -10.0, 10.0, 10.0]  # 在ground上随机分散20m x 20m范围

    # the default angles for all joints. key = joint name, value = target angle [rad]
    default_joint_angles = {
        "LF_HAA": 0.0,   # [rad]
        "RF_HAA": 0.0,   # [rad]
        "LH_HAA": 0.0,   # [rad]
        "RH_HAA": 0.0,   # [rad]
        "LF_HFE": 0.4,   # [rad]
        "RF_HFE": 0.4,   # [rad]
        "LH_HFE": -0.4,  # [rad]
        "RH_HFE": -0.4,  # [rad]
        "LF_KFE": -0.8,  # [rad]
        "RF_KFE": -0.8,  # [rad]
        "LH_KFE": 0.8,   # [rad]
        "RH_KFE": 0.8,   # [rad]
    }

@dataclass
class Commands:
    # 目标位置相对于机器人初始位置的偏移范围 [dx_min, dy_min, yaw_min, dx_max, dy_max, yaw_max]
    # dx/dy: 相对机器人初始位置的偏移（米）
    # yaw: 目标绝对朝向（弧度），水平方向随机
    pose_command_range = [-5.0, -5.0, -3.14, 5.0, 5.0, 3.14]

@dataclass
class Normalization:
    lin_vel = 2.0
    ang_vel = 0.25
    dof_pos = 1.0
    dof_vel = 0.05

@dataclass
class Asset:
    body_name = "base"
    foot_names = ["LF_FOOT", "RF_FOOT", "LH_FOOT", "RH_FOOT"]
    terminate_after_contacts_on = ["base"]
    ground_name = "ground"
   
@dataclass
class Sensor:
    base_linvel = "base_linvel"
    base_gyro = "base_gyro"

@dataclass
class RewardConfig:
    scales: dict[str, float] = field(
        default_factory=lambda: {
            "termination": -400.0,
            "position_tracking": 0.5,
            "fine_position_tracking": 0.5,
            "orientation": -0.2,
        }
    )

@registry.envcfg("anymal_c_navigation_flat")
@dataclass
class AnymalCEnvCfg(EnvCfg):
    model_file: str = model_file
    reset_noise_scale: float = 0.01
    max_episode_seconds: float = 10
    max_episode_steps: int = 1000
    sim_dt: float = 0.01
    ctrl_dt: float = 0.01
    reset_yaw_scale: float = 0.1
    max_dof_vel: float = 100.0  # 最大关节速度阈值，训练初期给予更大容忍度

    noise_config: NoiseConfig = field(default_factory=NoiseConfig)
    control_config: ControlConfig = field(default_factory=ControlConfig)
    reward_config: RewardConfig = field(default_factory=RewardConfig)
    init_state: InitState = field(default_factory=InitState)
    commands: Commands = field(default_factory=Commands)
    normalization: Normalization = field(default_factory=Normalization)
    asset: Asset = field(default_factory=Asset)
    sensor: Sensor = field(default_factory=Sensor)


# ==================== 复杂地形版本配置 ====================

model_file_terrain = os.path.dirname(__file__) + "/xmls/scene_terrain.xml"

@dataclass
class InitStateTerrain(InitState):
    """复杂地形特定的初始化配置"""
    # Z轴高度增加（因为高度场不是从0开始），会在reset中根据地形高度调整
    pos = [0.0, 0.0, 1.5]  # 初始高度更高，reset时会根据该位置的地形高度调整
    
    # 初始位置范围缩小，确保在生成的高度场范围内（高度字段size="20 20..."）
    pos_randomization_range = [-15.0, -15.0, 15.0, 15.0]  # 40m x 40m范围内

@dataclass
class CommandsTerrain(Commands):
    """复杂地形特定的命令配置"""
    # 目标位置范围也缩小
    pose_command_range = [-10.0, -10.0, -3.14, 10.0, 10.0, 3.14]

@dataclass
class RewardConfigTerrain(RewardConfig):
    """复杂地形的奖励配置"""
    scales: dict[str, float] = field(
        default_factory=lambda: {
            "termination": -400.0,
            "position_tracking": 0.5,
            "fine_position_tracking": 0.5,
            "orientation": -0.2,
            "climbing_reward": 0.1,        # 新增：爬坡奖励
            "steep_penalty": -0.2,          # 新增：陡坡惩罚
            "stability": -0.1,              # 新增：稳定性惩罚
        }
    )

@registry.envcfg("anymal_c_navigation_terrain")
@dataclass
class AnymalCEnvTerrainCfg(AnymalCEnvCfg):
    """复杂地形版本的环境配置"""
    model_file: str = model_file_terrain
    reset_noise_scale: float = 0.01
    max_episode_seconds: float = 15  # 地形复杂，允许更长的episode
    max_episode_steps: int = 1500
    sim_dt: float = 0.01
    ctrl_dt: float = 0.01
    reset_yaw_scale: float = 0.1
    max_dof_vel: float = 120.0  # 地形复杂，允许稍高的关节速度
    
    # 地形特定参数
    max_slope_angle: float = 45.0  # 最陡坡度角度（度）
    fall_height_threshold: float = 0.5  # 下降超过0.5m则终止
    
    init_state: InitStateTerrain = field(default_factory=InitStateTerrain)
    commands: CommandsTerrain = field(default_factory=CommandsTerrain)
    reward_config: RewardConfigTerrain = field(default_factory=RewardConfigTerrain)
    normalization: Normalization = field(default_factory=Normalization)
    asset: Asset = field(default_factory=Asset)
    sensor: Sensor = field(default_factory=Sensor)

