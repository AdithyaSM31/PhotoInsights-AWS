# Build Pillow Layer for AWS Lambda (Amazon Linux 2)
# This script uses Docker to build Pillow in the correct environment

FROM public.ecr.aws/lambda/python:3.11

# Install dependencies for Pillow
RUN yum install -y \
    libjpeg-devel \
    zlib-devel \
    freetype-devel \
    lcms2-devel \
    openjpeg2-devel \
    libtiff-devel \
    libwebp-devel \
    && yum clean all

# Create layer directory structure
RUN mkdir -p /opt/python

# Install Pillow
RUN pip install --target /opt/python Pillow==10.1.0

# Create the layer zip
WORKDIR /opt
RUN zip -r /pillow-layer.zip python/

CMD ["cat", "/pillow-layer.zip"]
