import { call } from './service.js';

export function requestReport(reportName, recIds) {
    call("FlrReport", "request_report", [reportName, recIds]).then(
        (resp) => {
            console.log(resp);
            var requestToken = resp.token;
            if(requestToken){
                downloadReport(requestToken);
            }
        }
    )
}

export function downloadReport(requestToken) {
    window.location = "/report/download?reqToken=" + requestToken;
}