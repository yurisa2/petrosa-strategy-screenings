import uvicorn


def main() -> None:
    uvicorn.run(
        app="app.app:router",
        host='0.0.0.0',
        port=8090,
        workers=1,
    )


if __name__ == "__main__":
    main()
