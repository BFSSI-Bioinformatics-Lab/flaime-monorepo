const encodeParams = (params) => {
    Object.keys(params).forEach(
        key => params[key] = params[key] instanceof Array ? 
            params[key].map(item => encodeURIComponent(item)) : 
            encodeURIComponent(params[key])
    );
    return params;
}

export function encodeQuery(func) {
    return async (params, ...args) => await func(encodeParams(params), ...args);
}

/* Provides a function to cancel a request */
export function addSignalController(req) {
    return () => {
        const abortController = new AbortController();
        return [async (args) => await req(args, abortController), () => abortController.abort()]
    }
}