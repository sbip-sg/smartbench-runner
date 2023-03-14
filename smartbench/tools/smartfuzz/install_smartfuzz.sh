BASEDIR=$(dirname "$0")

# Set up virtual environment venv
python3 -m venv smartfuzz_venv
source smartfuzz_venv/bin/activate

# Install requirements
pip install -e $BASEDIR/../../../smartfuzz/py-evm/
pip install -r $BASEDIR/../../../smartfuzz/requirements.txt
