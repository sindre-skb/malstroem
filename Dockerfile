FROM continuumio/miniconda3

WORKDIR /app

COPY environment.yml /app/environment.yml

RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "malstroem", "/bin/bash", "-c"]

COPY . /app

EXPOSE 5000
CMD ["conda", "run", "-n", "malstroem", "python", "app.py"]
