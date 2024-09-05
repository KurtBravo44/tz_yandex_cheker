from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import random


app = FastAPI()


# Модель для входных данных
class PhoneCheckRequest(BaseModel):
    phones: dict
    proxies: list


# Модель для результата проверки
class CheckResult(BaseModel):
    phone: str
    status: str


@app.post("/check_yandex_accounts", response_model=dict)
async def check_yandex_accounts(request: PhoneCheckRequest):
    results = {}
    for phone, id in request.phones.items():
        proxy = random.choice(request.proxies)
        try:
            status = await check_account(phone, proxy)
            results[phone] = status
        except Exception as e:
            results[phone] = "error"
            print(f"Error checking {phone} with proxy {proxy}: {e}")

    return results


async def check_account(phone: str, proxy: str) -> str:
    proxy_url = f"http://{proxy}"
    try:

        async with httpx.AsyncClient(proxies=proxy_url) as client:
            response = await client.get(f"https://passport.yandex.ru/auth/reg/portal?phone={phone}")

            # Проверяем ответ на наличие информации о регистрации
            if "номер телефона не зарегистрирован" in response.text:
                return "не зарегистрирован"
            elif "восстановление пароля" in response.text:
                return "зарегистрирован"
            else:
                raise Exception("Неизвестный ответ от Yandex")

    except httpx.ProxyError:
        return "Ошибка прокси"
    except httpx.RequestError as e:
        return f"Ошибка запроса: {e}"
    except Exception as e:
        return f"Произошла ошибка: {e}"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
