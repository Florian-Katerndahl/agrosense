FROM ghcr.io/osgeo/gdal:ubuntu-full-latest

LABEL org.opencontainers.image.authors="florian@katerndahl.com"

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y python3-poetry python3-pip python3-venv

WORKDIR /home/root/agrosense/

ADD bin/ bin/
ADD pyproject.toml .
ADD README.md .
ADD scenes/ scenes/

RUN poetry install --without workflow && \
    poetry build --format wheel

# feels a bit convoluted, but whatevers
RUN python3 -m venv /home/root/venv && \
    . /home/root/venv/bin/activate && \
    pip install /home/root/agrosense/dist/*.whl

WORKDIR /

ENV PATH="/home/root/venv/bin:$PATH"

CMD ["preprocess", " --help"]