import React, { useState, useEffect } from 'react';

import CalendarHeatmap from 'react-calendar-heatmap';
import 'react-calendar-heatmap/dist/styles.css';
import Axios from "axios";
import './GlucoseHeatMap.css';

const sendData = async () => {

    const  response = await Axios.post("http://127.0.0.1:8000/glucose-readings/",
        {
            "aggregation": "mean",
            "start_date": "2024-01-01",
            "end_date": "2024-01-08"
        }
    ); 
    // console.log(response)

    return response.data

};

export function GlucoseHeatMap() {

    (async () => {
        const res = await sendData();
        var data = res.data;
        
        data = data.replace("{", "")
        data = data.replace("[", "")
        data = data.replace("]", "")
        data = data.split("},");
        
        
        console.log(data);
    })();
    

    return (
        
        <div className='GlucoseHeatMap'>
            <CalendarHeatmap
                startDate={new Date('2016-01-01')}
                endDate={new Date('2016-04-01')}
                values={[
                { date: '2016-01-01', count: 12 },
                { date: '2016-01-22', count: 122 },
                { date: '2016-01-30', count: 38 }
                ]}
            />
            </div>
    )
}