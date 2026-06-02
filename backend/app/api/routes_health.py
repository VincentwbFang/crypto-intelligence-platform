from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "crypto-intelligence-platform",
    }


@router.get("/", include_in_schema=False)
def health_check_with_slash() -> dict[str, str]:
    return health_check()
