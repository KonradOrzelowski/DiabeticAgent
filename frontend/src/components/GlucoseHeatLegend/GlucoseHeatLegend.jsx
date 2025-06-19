import React from 'react';


export function GlucoseHeatLegend() {

    return (

            <div className='GlucoseHeatLegend'>
                <div className="sugar-legend">
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

    );
}
