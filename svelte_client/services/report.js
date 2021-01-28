import { call } from './service.js';

export function requestReport(reportName, recIds, callback) {
    call("FlrReport", "request_report", [reportName, recIds]).then(
        (resp) => {
            var requestToken = resp.token;
            if(requestToken){
                downloadReport(requestToken);
                if(callback){
                    callback();
                }
            }
        }
    )
}

export function downloadReport(requestToken) {
    let a = document.createElement("a");
    a.href = "/report/download?reqToken=" + requestToken;
    a.target = "blank";
    a.click();
}