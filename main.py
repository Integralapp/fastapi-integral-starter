import random
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
import requests
import uvicorn


class CustomMiddleware(BaseHTTPMiddleware):
    async def parse_api_req(self, request: Request) -> Response:
        payload = {
            "apiKey": request.headers.get("Authorization"),
            "ip": request.client.host,
            "method": request.method,
            "requestBody": await request.json() if request.json() else {},
            "headers": dict(request.headers),
            "path": request.url.path,
            "queryParams": dict(request.query_params),
        }

        int_headers = {
            "authorization": "02678855816446e2a2b2241cff9c77f9",
            "Integral-Application-Id": "fas.2BpopOs4MiZ0qazpbe5lfD"
        }

        int_response = requests.post(
            "http://localhost:4000/public/parse/pre-process", json=payload, headers=int_headers)

        return int_response

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Perform any pre-processing logic here
        print("Middleware: Before request")

        data = (await self.parse_api_req(request)).json()

        integral_req = data["request"]
        return_back_to_user = data["returnBackToUser"]
        status_code = data["statusCode"]
        user = data["user"]

        if (integral_req["hasResponseContent"]):
            return JSONResponse(content=return_back_to_user, status_code=status_code)

        request.state.integral_user = user

        response = await call_next(request)

        # Perform any post-processing logic here
        print("Middleware: After response")

        return response


app = FastAPI()


@app.post("/echo")
async def root(request: Request):
    u = request.state.integral_user
    return {"status": "live", "user": u}

# Apply the middleware to the app
app.add_middleware(CustomMiddleware)

# Run the app using Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
