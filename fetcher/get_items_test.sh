#!/usr/bin/env bash
# python mdz.py bsb10527954
echo -e "\nMDZ"
python mdz.py bsb10616989_00623_u001

echo -e "\nANNO"
python anno.py sam --min 18090101 --max 18090501
python anno.py vlb --min 18080101 --max 18080601

echo -e "\nABO"
python abo.py Z251542006
