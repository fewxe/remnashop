from . import main_menu, profile

routers = [
    main_menu.router,
    main_menu.dialog,
    profile.dialog,
]

__all__ = [
    "routers",
]
