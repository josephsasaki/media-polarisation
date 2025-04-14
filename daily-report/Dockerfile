FROM public.ecr.aws/lambda/python:3.9

WORKDIR ${LAMBDA_TASK_ROOT}

RUN mkdir template

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN yum install -y \
    libffi-devel \
    cairo \
    cairo-devel \
    pango \
    pango-devel \
    gdk-pixbuf2 \
    gdk-pixbuf2-devel \
    gcc \
    redhat-rpm-config \
    && yum clean all
    
ENV LD_LIBRARY_PATH="/opt/custom-libs/lib:${LD_LIBRARY_PATH}"

COPY template/jinja_template.html template/

COPY report_creator.py .

CMD [ "report_creator.lambda_handler" ]