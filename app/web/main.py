from fastapi import FastAPI, HTTPException
import uvicorn
import utils

app = FastAPI()

CACHE = {
}

CLOSE_NAME = "_Close"
WHITELIST = ["JPM", "WFC", "Citi", "BAC"]

class Plot:
    def __init__(self,name,image):
        self.name = name
        self.image = image
    
    def get_data(self):
        return {"name": self.name, "image": self.image}



@app.get("/", description="Возвращает информацию о приложении")
async def read_root():
    return {"Project": "Домашняя работа #4 по прикладному питону.", "Authors": ["Гарасев Никита Алексеевич", "Тишин Роман Вячеславович"]}

@app.get("/ping", description="ping - pong")
async def ping():
    return {"ping": "pong"}

@app.get("/cache", description="Возвращает кеш приложения")
async def get_cache():
    return CACHE

@app.delete("/cache", description="Очищает кеш приложения")
async def clear_cache():
    global CACHE
    CACHE = {}
    return {}

@app.get("/graph/{bank_name}", description="Возвращает STL разложение выбранного банка (JPM, WFC, Citi, BAC)")
async def get_graph(bank_name: str):
    if not bank_name in WHITELIST:
        return HTTPException(status_code=404, detail="Bank not found")
    target = bank_name + CLOSE_NAME
    image = utils.get_graph_plt(target)
    print(image)
    return Plot(target, image)


@app.get("/data/{date}", description="Возвращает значение из кеша или считывает из файла с предсказаниями")
async def get_data(date: str):
    global CACHE

    if date in CACHE:
        return CACHE[date]
    else:
        result = utils.get_forecast(date)
        CACHE[date] = result
        return result

@app.post("/data/{path}", description="Обновляет предсказания, подгрузжает новые из заданного файла")
async def post_data(path):
    if path != "last_forecast.csv": return HTTPException(status_code=404, detail="Bank not found")
    global CACHE
    CACHE = {}
    utils.get_new_forecast(path)
    return {"status": "Success"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)