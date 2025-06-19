import React, { useState, useEffect } from 'react';
import CalendarHeatmap from 'react-calendar-heatmap';
import { Tooltip } from 'react-tooltip';

import Axios from "axios";

import 'react-calendar-heatmap/dist/styles.css';
import './GlucoseHeatMap.css';


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
    const [heatmapData, setHeatmapData] = useState([]);

    useEffect(() => {
        async function fetchData() {
            let values = [];
            let dataForYears = {};

            const res = await sendData();
            const array = JSON.parse(res.data);
                
            for (let element of array) {
                const timestamp = new Date(element.date);
                const year = timestamp.getFullYear();
                
                if(!dataForYears.hasOwnProperty(year)){
                    dataForYears[year] = []
                }
                dataForYears[year].push({
                    date: new Date(element.date),
                    sgv: element.sgv,
                })
                
            }

            setDataForYears(dataForYears);

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

            <div className='GlucoseHeatLegend'>
                <div className="sugar-legend">
                    <div className="legend-item">
                        <svg className="color-box" width="20" height="20">
                            <rect width="20" height="20" className="color-empty" />
                        </svg>
                        <span>No Data</span>
                    </div>
                    <div className="legend-item">
                        <svg className="color-box" width="20" height="20">
                            <rect width="20" height="20" className="low-sugar" />
                        </svg>
                        <span>Below 50 (Low Sugar)</span>
                    </div>
                    <div className="legend-item">
                        <svg className="color-box" width="20" height="20">
                            <rect width="20" height="20" className="lower-in-range-sugar" />
                        </svg>
                        <span>50–79 (Lower In Range)</span>
                    </div>
                    <div className="legend-item">
                        <svg className="color-box" width="20" height="20">
                            <rect width="20" height="20" className="in-range-sugar" />
                        </svg>
                        <span>80–119 (In Range)</span>
                    </div>
                    <div className="legend-item">
                        <svg className="color-box" width="20" height="20">
                            <rect width="20" height="20" className="upper-in-range-sugar" />
                        </svg>
                        <span>120–139 (Upper In Range)</span>
                    </div>
                    <div className="legend-item">
                        <svg className="color-box" width="20" height="20">
                            <rect width="20" height="20" className="high-sugar" />
                        </svg>
                        <span>140–179 (High Sugar)</span>
                    </div>
                    <div className="legend-item">
                        <svg className="color-box" width="20" height="20">
                            <rect width="20" height="20" className="very-high-sugar" />
                        </svg>
                        <span>180–219 (Very High Sugar)</span>
                    </div>
                    <div className="legend-item">
                        <svg className="color-box" width="20" height="20">
                            <rect width="20" height="20" className="critical-sugar" />
                        </svg>
                        <span>220+ (Critical)</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
