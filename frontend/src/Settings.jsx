import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Save, ShieldAlert, BadgeCheck, Check } from 'lucide-react';
import { BASE_URL } from './api';

export default function Settings() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [success, setSuccess] = useState(false);

    const [formData, setFormData] = useState({
        risk_appetite: 'Moderate', // Conservative, Moderate, Aggressive
        max_position_size: 10,     // Percentage
        allowed_sectors: ['IT', 'Banking', 'Energy', 'Automobile']
    });

    const availableSectors = ['IT', 'Banking', 'Energy', 'Automobile', 'FMCG', 'Pharma', 'Metals'];

    useEffect(() => {
        fetch(`${BASE_URL}/api/settings/demo_user`)
            .then(r => r.json())
            .then(d => {
                setFormData({
                    risk_appetite:    d.risk_appetite    || 'Moderate',
                    max_position_size: d.max_position_size ?? 10,
                    allowed_sectors:  d.allowed_sectors  || ['IT', 'Banking', 'Energy', 'Automobile'],
                });
            })
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    const handleSectorToggle = (sector) => {
        setFormData(prev => ({
            ...prev,
            allowed_sectors: prev.allowed_sectors.includes(sector)
                ? prev.allowed_sectors.filter(s => s !== sector)
                : [...prev.allowed_sectors, sector]
        }));
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            // API call to the FastAPI implementation we define next
            const response = await fetch(`${BASE_URL}/api/settings/demo_user`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            if (!response.ok) throw new Error("Failed to save settings");

            setSuccess(true);
            setTimeout(() => setSuccess(false), 3000);
        } catch (error) {
            console.error(error);
            alert("Error saving settings.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-groww-light-gray text-groww-gray">
                <SettingsIcon className="animate-spin mr-2 outline-none" /> Initializing Control Center...
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-groww-light-gray font-sans text-groww-dark p-6 max-w-4xl mx-auto">

            <header className="mb-8">
                <h1 className="text-3xl font-bold tracking-tight text-groww-dark flex items-center">
                    <ShieldAlert className="mr-3 text-groww-green" size={28} /> Agent Control Center
                </h1>
                <p className="text-groww-gray mt-1">Configure trading constraints and boundary limits for the LangGraph Daemon.</p>
            </header>

            <div className="bg-dark-card rounded-xl border border-groww-gray/20 overflow-hidden shadow-sm mb-6">

                <div className="p-6 border-b border-groww-gray/10">
                    <h2 className="text-lg font-bold">Trading Constraints</h2>
                    <p className="text-sm text-groww-gray mt-1">Directly influences Superagent confidence scoring thresholds.</p>
                </div>

                <div className="p-6 space-y-8">

                    {/* Risk Level */}
                    <div>
                        <label className="block text-sm font-bold text-groww-dark mb-2">Risk Appetite</label>
                        <div className="grid grid-cols-3 gap-3">
                            {['Conservative', 'Moderate', 'Aggressive'].map(level => (
                                <button
                                    key={level}
                                    onClick={() => setFormData({ ...formData, risk_appetite: level })}
                                    className={`py-3 px-4 rounded-lg font-bold border transition-all ${formData.risk_appetite === level
                                            ? 'bg-groww-green/10 border-groww-green text-groww-green'
                                            : 'bg-dark-card border-groww-gray/20 text-groww-gray hover:border-groww-gray/50'
                                        }`}
                                >
                                    {level}
                                </button>
                            ))}
                        </div>
                        <p className="text-xs text-groww-gray mt-2 font-mono">
                            {formData.risk_appetite === 'Conservative' && "Agent requires >85% confidence to execute. Prefers large cap."}
                            {formData.risk_appetite === 'Moderate' && "Agent requires >70% confidence. Balanced approach."}
                            {formData.risk_appetite === 'Aggressive' && "Agent requires >55% confidence. High volatility acceptance."}
                        </p>
                    </div>

                    {/* Max Capital Per Trade */}
                    <div>
                        <label className="block text-sm font-bold text-groww-dark mb-2">
                            Max Capital Per Position ({formData.max_position_size}%)
                        </label>
                        <input
                            type="range"
                            min="1"
                            max="50"
                            value={formData.max_position_size}
                            onChange={(e) => setFormData({ ...formData, max_position_size: parseInt(e.target.value) })}
                            className="w-full accent-groww-green h-2 bg-groww-light-gray rounded-lg appearance-none cursor-pointer"
                        />
                    </div>

                    {/* Allowed Sectors */}
                    <div>
                        <label className="block text-sm font-bold text-groww-dark mb-2">Allowed Sectors</label>
                        <div className="flex flex-wrap gap-2">
                            {availableSectors.map(sector => {
                                const isSelected = formData.allowed_sectors.includes(sector);
                                return (
                                    <button
                                        key={sector}
                                        onClick={() => handleSectorToggle(sector)}
                                        className={`flex items-center px-4 py-2 rounded-full text-sm font-bold border transition-all ${isSelected
                                                ? 'bg-groww-dark text-white border-groww-dark'
                                                : 'bg-dark-card text-groww-gray border-groww-gray/20 hover:border-groww-gray/50'
                                            }`}
                                    >
                                        {isSelected && <Check size={14} className="mr-1" />} {sector}
                                    </button>
                                )
                            })}
                        </div>
                    </div>

                </div>

                <div className="p-6 bg-groww-light-gray/30 border-t border-groww-gray/10 flex items-center justify-between">
                    <div className="flex items-center">
                        {success && <span className="text-groww-green font-bold text-sm flex items-center animate-fade-in"><BadgeCheck size={18} className="mr-1" /> Dynamic Rules Updated</span>}
                    </div>
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="px-6 py-2 bg-groww-green hover:bg-[#00b386] text-white font-bold rounded-lg transition-colors flex items-center disabled:opacity-50"
                    >
                        {saving ? <SettingsIcon size={18} className="animate-spin" /> : <Save size={18} className="mr-2" />}
                        {saving ? 'Syncing...' : 'Save Configuration'}
                    </button>
                </div>

            </div>

        </div>
    );
}
