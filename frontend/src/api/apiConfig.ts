import { CONFIG } from "@/const";
import axios, { AxiosRequestConfig } from "axios";


export async function get<T>(url: string, axiosOption: AxiosRequestConfig): Promise<T> {
    try {
        const { protocol, hostname, port } = window.location;

        CONFIG.apiURL = `${protocol}//${hostname}${port ? ':' + port : ''}` + '/api/v1/';
        const response = await axios.get<T>(CONFIG.apiURL + url, axiosOption);
        if ([200, 201].includes(response.status)) {
            return response.data;
        }
        throw new Error("Api Error " + JSON.stringify(response.data));

    } catch (error) {
        console.error(error);
        return null as unknown as T;
    }
}

export async function post<T>(url: string, data: object, axiosOption: AxiosRequestConfig): Promise<T> {
    try {
        const { protocol, hostname, port } = window.location;

        CONFIG.apiURL = `${protocol}//${hostname}${port ? ':' + port : ''}` + '/api/v1/';

        const response = await axios.post<T>(CONFIG.apiURL + url, data, axiosOption);

        if ([200, 201].includes(response.status)) {
            return response.data;
        }

        throw new Error("Api Error " + JSON.stringify(response.data));
    } catch (error) {
        console.error(error);
        return null as unknown as T;
    }
}

export async function put<T>(url: string, data: object, axiosOption: AxiosRequestConfig): Promise<T> {
    try {
        const { protocol, hostname, port } = window.location;

        CONFIG.apiURL = `${protocol}//${hostname}${port ? ':' + port : ''}` + '/api/v1/';

        const response = await axios.put<T>(CONFIG.apiURL + url, data, axiosOption);

        if ([200, 201].includes(response.status)) {
            return response.data;
        }

        throw new Error("Api Error " + JSON.stringify(response.data));
    } catch (error) {
        console.error(error);
        return null as unknown as T;
    }
}

const api = {
    get,
    post,
    put
}

export default api;
