FROM continuumio/miniconda3

WORKDIR /app

COPY environment.yml /app/environment.yml

RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "malstroem-env", "/bin/bash", "-c"]

COPY . /app

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "malstroem-env", "python", "your_script.py"]
