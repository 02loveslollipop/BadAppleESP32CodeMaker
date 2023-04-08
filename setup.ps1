call conda create -n "BadAppleCodeCreator"  python=3.9
call conda activate BadAppleCodeCreator
python -m  pip install -r ".\requirements.txt"
python -m  setup build_ext --inplace