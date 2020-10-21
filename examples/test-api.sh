#!/bin/bash

test_all=0

if [[ $# == 0 ]]; then
	test_all=1
fi

if [[ $1 == 1 ]] || [[ "$test_all" = 1 ]]; then
	curl -X POST "http://localhost:8000/forecast?file_url=file:///home/sapronov/Work/mmk/debug/gasopt-lib/examples/test_data/gas-expense-10.19.xlsx&file_md5=48859b9052f25c4c3d752e567dcc8cc9&shop_code=lpc10"
fi

if [[ $1 == 2 ]] || [[ "$test_all" = 1 ]]; then
	curl  -X GET "http://localhost:8000/forecast?date_st=2019-11-01&days_cnt=3&furn_id=1&shop_code=lpc10"
fi

if [[ $1 == 3 ]] || [[ "$test_all" = 1 ]]; then
	#curl -i -H "Content-Type: application/json"  -X POST -d '{"slabs":1}' "http://localhost:8000/optimize?furn_id=1"

	#curl -H "Content-Type: application/json"  -X POST -d '{"slabs":[{"length_s":4800,"width_s":1340,"weight_s":12.273,"slab_temp":112.0,"l_thick":2.0,"dt_prev":0.007,"row":2,"mark":"other"}'  "http://localhost:8000/optimize?furn_id=1"
	curl -H "Content-Type: application/json"  -X POST -d '{"slabs":[{"length_s":4800,"width_s":1340,"weight_s":12.273,"slab_temp":112.0,"l_thick":2.0,"dt_prev":0.007,"row":2,"mark":"other"}]}' "http://localhost:8000/optimize?furn_id=1"
fi
