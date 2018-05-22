# python3-base-image
Python 3 language support for Dispatch

Latest image [on Docker Hub](https://hub.docker.com/r/dispatchframework/python3-base/): `dispatchframework/python3-base:0.0.6`

## Usage

You need a recent version of Dispatch [installed in your Kubernetes cluster, Dispatch CLI configured](https://vmware.github.io/dispatch/documentation/guides/quickstart) to use it.

### Adding the Base Image

To add the base-image to Dispatch:
```bash
$ dispatch create base-image python3-base dispatchframework/python3-base:0.0.6
```

Make sure the base-image status is `READY` (it normally goes from `INITIALIZED` to `READY`):
```bash
$ dispatch get base-image python3-base
```

### Adding Runtime Dependencies

Library dependencies listed in `requirements.txt` ([pip dependency manifest](https://pip.pypa.io/en/stable/user_guide/#requirements-files)) need to be wrapped into a Dispatch image. For example, suppose we need a HTTP library:

```bash
$ cat ./requirements.txt
```
```
requests
```
```bash
$ dispatch create image python3-mylibs python3-base --runtime-deps ./requirements.txt
```

Make sure the image status is `READY` (it normally goes from `INITIALIZED` to `READY`):
```bash
$ dispatch get image python3-mylibs
```


### Creating Functions

Using the python3 base-image, you can create Dispatch functions from python source files. The file can require any libraries from the image (see above).

The only requirement is: a function called **`handle`** must be defined that accepts 2 arguments (`context` and `payload`), for example:  
```bash
$ cat ./http.py
```
```python
import requests

def handle(context, payload):
    url = payload.get("url", "http://example.com")
    resp = requests.get(url)
    return {"status": resp.status_code}
```

```bash
$ dispatch create function python3-mylibs http ./http.py
```

Make sure the function status is `READY` (it normally goes from `INITIALIZED` to `READY`):
```bash
$ dispatch get function http
```

### Running Functions

As usual:

```bash
$ dispatch exec --json --input '{"url": "http://dispatchframework.io"}' --wait http
```
```json
{
    "blocking": true,
    "executedTime": 1524768025,
    "faasId": "09e3c92a-a9e5-438c-b627-84a100c041d5",
    "finishedTime": 1524768025,
    "functionId": "6f5d49a6-3a5a-43d2-ab60-7bef6b3d0b71",
    "functionName": "http",
    "input": {
        "url": "http://dispatchframework.io"
    },
    "logs": {
        "stderr": null,
        "stdout": null
    },
    "name": "e7ef9a88-ff3e-48b6-a331-b350dbde293e",
    "output": {
        "status": 200
    },
    "reason": null,
    "secrets": [],
    "services": null,
    "status": "READY",
    "tags": []
}
```

## Error Handling

There are three types of errors that can be thrown when invoking a function:
* `InputError`
* `FunctionError`
* `SystemError`

`SystemError` represents an error in the Dispatch infrastructure. `InputError` represents an error in the input detected either early in the function itself or through input schema validation. `FunctionError` represents an error in the function logic or an output schema validation error.

Functions themselves can either throw `InputError` or `FunctionError`

### Input Validation

For Python, the following exceptions thrown from the function are considered `InputError`:
* **`ValueError`**
* **`TypeError`**

All other exceptions thrown from the function are considered `FunctionError`.

To validate input in the function body:
```python
def lower(ctx, payload):
    if type(payload) is not str:
        raise TypeError("payload is not of type str")

    return payload.lower()
```

### Note

Since **`ValueError`** and **`TypeError`** are considered `InputError`, functions should not throw them unless explicitly thrown due to an input validation error. Functions should catch and handle them accordingly if they should not be classified as `InputError`. 