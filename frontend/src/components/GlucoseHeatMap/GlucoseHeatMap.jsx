import React, { useState, useEffect } from 'react';
import CalendarHeatmap from 'react-calendar-heatmap';
import { Tooltip } from 'react-tooltip';


import Axios from "axios";

import 'react-calendar-heatmap/dist/styles.css';
import './GlucoseHeatMap.css';

const sendData = async () => {
    const response = await Axios.post("http://127.0.0.1:8000/glucose-readings/", {
        "aggregation": "mean",
        "start_date": "2024-01-01",
        "end_date": "2024-01-08"
    });
    return response.data;
};

export function GlucoseHeatMap() {
    const [heatmapData, setHeatmapData] = useState([]);
    const [minDate, setMinDate] = useState(null);
    const [maxDate, setMaxDate] = useState(null);

    useEffect(() => {
        async function fetchData() {
            let values = [];

            const res = await sendData();
            const array = JSON.parse(res.data);

            let min = Infinity;
            let max = -Infinity;

            for (let element of array) {
                const timestamp = Date.parse(element.date);
                if (timestamp < min) min = timestamp;
                if (timestamp > max) max = timestamp;
                
                console.log(element.sgv)
                values.push({
                    date: new Date(element.date),
                    sgv: element.sgv,
                });
            }
            console.log(values)
            setHeatmapData(values);
            setMinDate(new Date(min));
            setMaxDate(new Date(max));

            console.log(heatmapData)
        }

        fetchData();
    }, []);

    return (
        <div className='GlucoseHeatMap'>
            <CalendarHeatmap

            startDate={minDate}
            endDate={maxDate}
            values={heatmapData}
            classForValue={value => {
                if (!value) return 'color-empty';
                return `color-github-${value.sgv % 4}`;
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



        </div>
    );
}
