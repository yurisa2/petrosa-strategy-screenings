import uvicorn


def main() -> None:
    uvicorn.run(
        app="app.app:home_router",
        host='0.0.0.0',
        port=8080,
        workers=1,
    )


if __name__ == "__main__":
    main()
