import React, { useState, useEffect } from 'react';
import CalendarHeatmap from 'react-calendar-heatmap';
import { Tooltip } from 'react-tooltip';

import Axios from "axios";

import 'react-calendar-heatmap/dist/styles.css';
import './GlucoseHeatMap.css';
import { GlucoseHeatLegend } from "../GlucoseHeatLegend/GlucoseHeatLegend";

async function sendData(){
    const response = await Axios.post("http://127.0.0.1:8000/glucose-readings/", {
        "aggregation": "mean",
        "start_date": "2022-08-21",
        "end_date": "2025-01-01"
    });
    return response.data;
};

export function GlucoseHeatMap() {
    const [dataForYears, setDataForYears] = useState([]);

    useEffect(() => {
        async function fetchData() {
            let dataForYears = {};

            const res = await sendData();
            const array = JSON.parse(res.data);

            const start = Date.now();


            for (let element of array) {
                const timestamp = new Date(element.date);
                const year = timestamp.getFullYear();
                
                if(!dataForYears.hasOwnProperty(year)){
                    dataForYears[year] = []
                }
                dataForYears[year].push({
                    date: timestamp,
                    sgv: element.sgv,
                })
                
            }

            setDataForYears(dataForYears);

  
            const end = Date.now();
            console.log(`Time taken: ${end - start} ms`);

        }

        fetchData();
    }, []);

    return (
        <div className='GlucoseHeatMaps'>
            <div className='GlucoseHeatMap'>
            {Object.keys(dataForYears).map(key => (<div>
                <h3>{`${key}`}</h3>
                <CalendarHeatmap
                
                
                    startDate={new Date(`01-01-${key}`)}
                    endDate={new Date(`12-31-${key}`)}
                    values={dataForYears[key]}
                    classForValue={value => {
                        try{
                            if (!value.sgv) return 'color-empty';
                            if (50 > value.sgv) return 'low-sugar';
                            if (50 <= value.sgv && value.sgv < 80) return 'lower-in-range-sugar';
                            if (80 <= value.sgv && value.sgv < 120) return 'in-range-sugar';
                            if (120 <= value.sgv && value.sgv < 140) return 'upper-in-range-sugar';
                            if (140 <= value.sgv && value.sgv < 180) return 'high-sugar';
                            if (180 <= value.sgv && value.sgv < 220) return 'very-high-sugar';
                            if (220 <= value.sgv) return 'critical-sugar';
                            return 'color-empty'; 
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
            </div>))}
            <Tooltip id="glucose-tooltip" place="top" />
        </div>

            <GlucoseHeatLegend/>
        </div>
    );
}
