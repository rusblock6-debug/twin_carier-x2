
window.TimeUtils = {
    utcToLocal: function(utcString) {
        if (!utcString) return '';
        const date = new Date(utcString);
        const offset = date.getTimezoneOffset() * 60000;
        const localDate = new Date(date.getTime() - offset);
        return localDate.toISOString().slice(0, 16);
    },
    
    localToUtc: function(localString) {
        if (!localString) return '';

        const date = new Date(localString);

        const year = date.getUTCFullYear();
        const month = date.getUTCMonth();
        const day = date.getUTCDate();
        const hours = date.getUTCHours();
        const minutes = date.getUTCMinutes();

        const utcDate = new Date(Date.UTC(year, month, day, hours, minutes));

        return utcDate.toISOString();
    }
};