FROM python:3.8 as base
WORKDIR /usr/src/app
ENV VIRTUAL_ENV=/venv

FROM base as builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
RUN pip install --pre poetry
RUN python -m venv $VIRTUAL_ENV
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | $VIRTUAL_ENV/bin/pip install -r /dev/stdin
COPY . .
RUN poetry build && $VIRTUAL_ENV/bin/pip install dist/*.whl

FROM base as final
COPY --from=builder /venv /venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENTRYPOINT [ "crawler" ]
