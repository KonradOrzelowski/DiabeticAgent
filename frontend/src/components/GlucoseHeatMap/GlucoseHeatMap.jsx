import React, { useState, useEffect } from 'react';
import CalendarHeatmap from 'react-calendar-heatmap';
import { Tooltip } from 'react-tooltip';


import Axios from "axios";

import 'react-calendar-heatmap/dist/styles.css';
import './GlucoseHeatMap.css';

const sendData = async () => {
    const response = await Axios.post("http://127.0.0.1:8000/glucose-readings/", {
        "aggregation": "mean",
        "start_date": "2022-08-21",
        "end_date": "2025-01-01"
    });
    return response.data;
};

export function GlucoseHeatMap() {
    const [boo, setBoo] = useState([]);
    const [heatmapData, setHeatmapData] = useState([]);
    const [minDate, setMinDate] = useState(null);
    const [maxDate, setMaxDate] = useState(null);

    useEffect(() => {
        async function fetchData() {
            let values = [];
            let boo = {};

            const res = await sendData();
            const array = JSON.parse(res.data);

            let min = Infinity;
            let max = -Infinity;

            for (let element of array) {
                const timestamp = new Date(element.date);
                const year = timestamp.getFullYear();
                
                if(!boo.hasOwnProperty(year)){
                    boo[year] = []
                }
                boo[year].push({
                    date: new Date(element.date),
                    sgv: element.sgv,
                })

                if (timestamp < min) min = timestamp;
                if (timestamp > max) max = timestamp;
                
                values.push({
                    date: new Date(element.date),
                    sgv: element.sgv,
                });
            }

            console.log(boo)
            setBoo(boo)
            setHeatmapData(values);
            setMinDate(new Date(min));
            setMaxDate(new Date(max));

        }

        fetchData();
    }, []);

    return (
        


        <div className='GlucoseHeatMap'>
            {
                Object.keys(boo).map(key => (
                    console.log(boo[key])
                ))
            }

            {/* <CalendarHeatmap

                startDate={minDate}
                endDate={maxDate}
                values={heatmapData}
                classForValue={value => {
                    try{
                        if (!value.sgv) return 'color-empty';
                        if (value.sgv < 50) return 'low-sugar';
                        if (value.sgv >= 50 && value.sgv < 80) return 'lower-in-range-sugar';
                        if (value.sgv >= 100 && value.sgv < 120) return 'in-range-sugar';
                        if (value.sgv >= 120 && value.sgv < 140) return 'upper-in-range-sugar';
                        if (value.sgv > 140 && value.sgv < 180) return 'high-sugar';
                        if (value.sgv >= 180) return 'very-high-sugar';
                        return 'risen-sugar'; // Fallback or you can adjust this logic
                    }
                    catch(e){
                        return 'color-empty';
                    }
                    
                }}
                tooltipDataAttrs={value => {
                    if (!value || !value.date) return {};
                    return {
                    'data-tooltip-id': 'glucose-tooltip',
                    'data-tooltip-content': `Date: ${value.date.toISOString().slice(0, 10)} | SGV: ${value.sgv}`,
                    };
                }}
                showWeekdayLabels={true} 
            
            />

            <Tooltip id="glucose-tooltip" place="top" />
            */}



        </div>
    );
}
