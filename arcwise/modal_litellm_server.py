import subprocess
import modal
from modal.app import App
from modal.partial_function import web_server

image = (
    modal.Image.debian_slim()
    .pip_install("litellm[proxy]", "boto3")
    .copy_local_file("litellm_config.yaml", "/litellm_config.yaml")
)


app = App()


@app.function(secrets=[modal.Secret.from_name("litellm_secrets")], image=image)
@web_server(4000)
def litellm_proxy():

    subprocess.Popen("litellm --config /litellm_config.yaml", shell=True)
