import asyncio


async def main():
    """
    Функция показывающая, что контейнер запускается корректно. Если оставлять пустой файл, то контейнер сразу гасится,
    т.к. операций для выполнения больше нет.
    """
    print('hello')
    await asyncio.sleep(99999999999)
    print('world')

asyncio.run(main())
