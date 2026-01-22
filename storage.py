# { "Depends": "py-genlayer:latest" }

from genlayer import *

class HelloGenLayer(gl.Contract):
    greeting: str

    def __init__(self):
        self.greeting = "hello genlayer"

    @gl.public.view
    def say_hello(self, name: str) -> str:
        return f"{self.greeting}, {name}"

    @gl.public.write
    def update_greeting(self, new_greeting: str) -> None:
        self.greeting = new_greeting
