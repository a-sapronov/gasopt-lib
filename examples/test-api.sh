#!/bin/bash

test_all=0

if [[ $# == 0 ]]; then
	test_all=1
fi

if [[ $1 == 1 ]] || [[ "$test_all" = 1 ]]; then
	curl -X POST "http://localhost:8000/forecast?file_url=file:///home/sapronov/work/mmk/gasopt-lib/examples/test_data/gas-expense-10.19.xlsx&file_md5=48859b9052f25c4c3d752e567dcc8cc9&shop_code=lpc10"
fi

if [[ $1 == 2 ]] || [[ "$test_all" = 1 ]]; then
	curl  -X GET "http://localhost:8000/forecast?days_offset=0&days_cnt=2&furn_id=1&shop_code=lpc10"
fi

if [[ $1 == 3 ]] || [[ "$test_all" = 1 ]]; then
	#curl -i -H "Content-Type: application/json"  -X POST -d '{"slabs":1}' "http://localhost:8000/optimize?furn_id=1"

	curl -H "Content-Type: application/json"  -X POST -d '{"slabs":[{"length_s":4800,"width_s":1340,"weight_s":12.273,"slab_temp":112.0,"l_thick":2.0,"dt_prev":0.007,"row":2,"mark":"??3??"},{"length_s":4800,"width_s":1340,"weight_s":12.24,"slab_temp":745.0,"l_thick":2.0,"dt_prev":134.657,"row":1,"mark":"??3??"},{"length_s":4800,"width_s":1340,"weight_s":12.24,"slab_temp":720.0,"l_thick":2.0,"dt_prev":0.003,"row":2,"mark":"??3??"},{"length_s":5000,"width_s":1340,"weight_s":12.78,"slab_temp":243.0,"l_thick":2.0,"dt_prev":235.523,"row":1,"mark":"??3??"},{"length_s":5000,"width_s":1340,"weight_s":12.78,"slab_temp":242.0,"l_thick":2.0,"dt_prev":0.01,"row":2,"mark":"??3??"},{"length_s":5000,"width_s":1340,"weight_s":12.784,"slab_temp":434.0,"l_thick":2.0,"dt_prev":596.834,"row":1,"mark":"??3??"},{"length_s":6000,"width_s":1270,"weight_s":14.54,"slab_temp":672.0,"l_thick":2.5,"dt_prev":0.003,"row":2,"mark":"other"},{"length_s":6000,"width_s":1270,"weight_s":14.54,"slab_temp":55.0,"l_thick":2.5,"dt_prev":371.59,"row":1,"mark":"other"},{"length_s":6000,"width_s":1270,"weight_s":14.54,"slab_temp":280.0,"l_thick":2.5,"dt_prev":0.003,"row":2,"mark":"other"},{"length_s":9500,"width_s":1340,"weight_s":24.24,"slab_temp":507.0,"l_thick":2.0,"dt_prev":176.357,"row":2,"mark":"??3??"}]}' "http://localhost:8000/optimize?furn_id=1"
fi
