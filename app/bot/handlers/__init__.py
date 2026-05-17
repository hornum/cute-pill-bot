from aiogram import Router
from .start import router as start_router
from .medicines import router as medicines_router
from .medicines_edit import router as medicines_edit_router
from .medicines_delete import router as medicines_delete_router
from .reminders import router as reminders_router


router = Router()

router.include_router(start_router)
router.include_router(medicines_router)
router.include_router(reminders_router)
router.include_router(medicines_edit_router)
router.include_router(medicines_delete_router)
