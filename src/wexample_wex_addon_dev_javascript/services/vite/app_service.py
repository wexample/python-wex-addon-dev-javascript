from __future__ import annotations

from wexample_wex_addon_ai.service.agent_contributing_service_mixin import (
    AgentContributingServiceMixin,
)
from wexample_wex_addon_app.service.app_service import AppService as BaseAppService


class AppService(BaseAppService, AgentContributingServiceMixin):
    """Vite AppService — composes the base service surface with the agent-contribution mixin.

    Picked up by `AppAddonManager.get_app_service('vite', ...)` because this file is named
    `app_service.py` next to `service.yml`. The mixin makes the agents declared under
    `ai/agents/<name>/agent.yml` discoverable by `wex talk` / `/sessions`.
    """
