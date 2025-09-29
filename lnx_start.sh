#!/bin/bash

echo
echo "?? �Ұ� Interval Timer MVP �M�ס]Linux�^"
echo "=========================================="

# �����ܸ}���Ҧb�ؿ�
cd "$(dirname "$0")"

# Step 1: �T�O Python3 �s�b
if ! command -v python3 &>/dev/null; then
  echo "? �Х��w�� Python3"
  exit 1
fi

# Step 2: �ˬd pip
if ! command -v pip3 &>/dev/null; then
  echo "? pip3 ���w�ˡA�Х��w�� pip"
  exit 1
fi

# Step 3: �w�� requirements.txt ���M��]�ȲĤ@���ݭn�^
echo "?? �w�� Python �̿�]requirements.txt�^..."
pip3 install -r requirements.txt

# Step 4: ����E���]�p�G�O�즸���p�^
echo "?? ���� Django ��Ʈw�E��..."
# python3 manage.py makemigrations timers
# python3 manage.py migrate

sudo nginx -t
sudo systemctl reload nginx

# Step 5: �Ұʦ��A��
echo "?? �Ұ� Django ���A���Ghttp://0.0.0.0:8000"
# python3 manage.py runserver 0.0.0.0:8000

gunicorn intervaltimer.wsgi:application --bind 0.0.0.0:8000

