FROM ubuntu:22.04 AS base

WORKDIR /ai_server

ENV DEBIAN_FRONTEND=noninteractive
ENV ROC_ENABLE_PRE_VEGA=1
ENV AMD_SERIALIZE_KERNEL=3
ENV TORCH_USE_HIP_DSA=1

RUN apt update && apt install software-properties-common -y
RUN apt-get update &&\
	apt-get install \
		gcc\
		git\
		curl\
		ffmpeg\
		libsm6\
		libxext6\
		poppler-utils\
		apt-transport-https\
		wget\
		libjpeg-dev\
		python3-dev\
		cmake\
		python3-pip\
		python3.10 -y

RUN pip install --no-cache-dir wheel setuptools
RUN pip3 install --no-cache-dir --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm6.1/

#RUN wget -O key.apt https://notesalexp.org/debian/alexp_key.asc && apt-key add key.apt
#RUN apt update && apt install tesseract-ocr -y

RUN wget -qO - https://repo.radeon.com/rocm/rocm.gpg.key | tee /usr/share/keyrings/rocm.gpg.key && \
    echo "deb [signed-by=/usr/share/keyrings/rocm.gpg.key] http://repo.radeon.com/rocm/apt/5.7.1 ubuntu main" | tee /etc/apt/sources.list.d/rocm.list

RUN apt update && apt install -y linux-headers-generic

RUN apt update && apt install -y python3-setuptools python3-wheel && \
	rm -f /etc/apt/sources.list.d/rocm.list &&\
    wget https://repo.radeon.com/amdgpu-install/6.3.3/ubuntu/jammy/amdgpu-install_6.3.60303-1_all.deb && \
    apt install -y ./amdgpu-install_6.3.60303-1_all.deb && \
    apt update
RUN amdgpu-install --usecase=hip,graphics,rocm --no-dkms -y

RUN hipcc --version

RUN wget -q --show-progress https://repo.radeon.com/rocm/manylinux/rocm-rel-6.3.4/torch-2.4.0%2Brocm6.3.4.git7cecbf6d-cp310-cp310-linux_x86_64.whl &&\
	wget -q --show-progress https://repo.radeon.com/rocm/manylinux/rocm-rel-6.3.4/torchvision-0.19.0%2Brocm6.3.4.gitfab84886-cp310-cp310-linux_x86_64.whl &&\
	wget -q --show-progress https://repo.radeon.com/rocm/manylinux/rocm-rel-6.3.4/pytorch_triton_rocm-3.0.0%2Brocm6.3.4.git75cc27c2-cp310-cp310-linux_x86_64.whl &&\
	wget -q --show-progress https://repo.radeon.com/rocm/manylinux/rocm-rel-6.3.4/torchaudio-2.4.0%2Brocm6.3.4.git69d40773-cp310-cp310-linux_x86_64.whl

RUN git clone --recurse https://github.com/ROCm/bitsandbytes &&\
	cd bitsandbytes &&\
	git checkout rocm_enabled &&\
	pip install --no-cache-dir --ignore-installed --no-deps -r requirements-dev.txt &&\
	cmake -DCOMPUTE_BACKEND=hip -DBNB_ROCM_ARCH="gfx1032" -S . &&\
	make &&\
	pip install --ignore-installed --no-cache-dir --no-deps .

COPY ./requirements.txt /ai_server
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --force-reinstall pytorch-triton-rocm==3.0.0 --index-url https://download.pytorch.org/whl/nightly/rocm6.3

RUN rm -rf *.whl
RUN rm -rf *.deb
RUN rm -rf bitsandbytes/
RUN rm -rf *.apt

COPY ./ /ai_server/

CMD [ "python3", "app.py" ]
