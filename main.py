from fastapi import FastAPI
from pydantic import BaseModel
import requests
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
    print(proxy_url)
    try:
        response = requests.get(
            f"https://passport.yandex.ru/auth/reg/portal?phone={phone}",
            proxies={"https": proxy_url},
            timeout=10 # Установка таймаута для запроса
        )

        decoded_string = response.text.encode('latin1').decode('utf-8')


        # Проверяем ответ на наличие информации о регистрации
        if "не зарегистрирован" in decoded_string:
            return "не зарегистрирован"
        elif "подтверждение" in decoded_string:
            return "зарегистрирован"
        else:
            raise Exception("Неизвестный ответ от Yandex")

    except requests.exceptions.ProxyError as e:
        print(e)
        return "Ошибка прокси"
    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {e}"
    except Exception as e:
        return f"Произошла ошибка: {e}"


if __name__ == "main":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)