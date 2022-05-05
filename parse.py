import csv
import os
import re

class Parse:
    def __init__(self, interval, log_file):
        self.interval = int(interval)
        self.log_file = log_file

    def parse_ram(self, lookup_table, ram):
        lookup_table['Used RAM (MB)'] = float(ram[0])
        lookup_table['Total RAM (MB)'] = float(ram[1])
        lookup_table['Number of Free RAM Blocks'] = float(ram[2])
        lookup_table['Size of Free RAM Blocks (MB)'] = float(ram[3])
        return lookup_table

    def parse_swap(self, lookup_table, swap):
        lookup_table['Used SWAP (MB)'] = float(swap[0])
        lookup_table['Total SWAP (MB)'] = float(swap[1])
        lookup_table['Cached SWAP (MB)'] = float(swap[2])
        return lookup_table

    def parse_iram(self, lookup_table, iram):
        lookup_table['Used IRAM (kB)'] = float(iram[0])
        lookup_table['Total IRAM (kB)'] = float(iram[1])
        lookup_table['Size of IRAM Blocks (kB)'] = float(iram[2])
        return lookup_table

    def parse_cpus(self, lookup_table, cpus):
        frequency = re.findall(r'@([0-9]*)', cpus)
        lookup_table['CPU Frequency (MHz)'] = float(frequency[0]) if frequency else ''
        max = 0
        for i, cpu in enumerate(cpus.split(',')):
            percent = cpu.split('%')[0]
            if percent != "off":
                if int(percent) > max:
                    max = int(percent)
            else:
                continue
            lookup_table[f'CPU {i} Load (%)'] = percent
        lookup_table['CPU Load max'] = max
        return lookup_table

    def parse_gr3d(self, lookup_table, gr3d):
        lookup_table['Used GR3D (%)'] = float(gr3d[0])
        lookup_table['GR3D Frequency (MHz)'] = float(gr3d[1]) if gr3d[1] else ''
        return lookup_table

    def parse_emc(self, lookup_table, emc):
        lookup_table['Used EMC (%)'] = float(emc[0])
        lookup_table['GR3D Frequency (MHz)'] = float(emc[1])  if emc[1] else ''
        return lookup_table

    def parse_temperatures(self, lookup_table, temperatures):
        for label, temperature in temperatures:
            lookup_table[f'{label} Temperature (C)'] = float(temperature)
        return lookup_table

    def parse_vdds(self, lookup_table, vdds):
        for label, curr_vdd, avg_vdd in vdds:
            lookup_table[f'Current {label} Power Consumption (mW)'] = float(curr_vdd)
        return lookup_table

    def parse_vdd_cpu(self, lookup_table, vdd):
        lookup_table['CPU Power (mW)'] = float(vdd[0][0])
        return lookup_table

    def parse_vdd_gpu(self, lookup_table, vdd):
        lookup_table['GPU Power (mW)'] = float(vdd[0][0])
        return lookup_table

    def parse_vdd_ddr(self, lookup_table, vdd):
        lookup_table['DDR Power (mW)'] = float(vdd[0][0])
        return lookup_table

    def parse_data(self, line, filename):
        lookup_table = {}

        cpus = re.findall(r'CPU \[(.*)\]', line)
        self.parse_cpus(lookup_table, cpus[0]) if cpus else None

        gr3d = re.findall(r'GR3D_FREQ ([0-9]*)%@?([0-9]*)?', line)
        self.parse_gr3d(lookup_table, gr3d[0]) if gr3d else None

        vdd_sys_soc = re.findall(r'VDD_SYS_SOC ([0-9]*)\/([0-9]*)', line)
        vdd_sys_soc = float(vdd_sys_soc[0][0])

        vdd_4v0_wifi = re.findall(r'VDD_4V0_WIFI ([0-9]*)\/([0-9]*)', line)
        vdd_4v0_wifi = float(vdd_4v0_wifi[0][0])

        vdd_sys_cpu = re.findall(r'VDD_SYS_CPU ([0-9]*)\/([0-9]*)', line)
        self.parse_vdd_cpu(lookup_table, vdd_sys_cpu) if vdd_sys_cpu else None

        vdd_sys_gpu = re.findall(r'VDD_SYS_GPU ([0-9]*)\/([0-9]*)', line)
        self.parse_vdd_gpu(lookup_table, vdd_sys_gpu) if vdd_sys_gpu else None

        vdd_sys_ddr = re.findall(r'VDD_SYS_DDR ([0-9]*)\/([0-9]*)', line)
        self.parse_vdd_ddr(lookup_table, vdd_sys_ddr) if vdd_sys_ddr else None

        cpu_gpu_ddr = lookup_table['CPU Power (mW)'] + lookup_table['GPU Power (mW)'] + lookup_table['DDR Power (mW)']

        total_power = cpu_gpu_ddr + vdd_sys_soc + vdd_4v0_wifi
        lookup_table['Total Power (mW)'] = total_power

        return lookup_table

    def create_header(self, line, filename):
        labels = ['Index', 'Time (mS)'] + list(self.parse_data(line, filename).keys())
        return labels

    def parse_filename(self, filename):
        split_filename = filename.split("_")
        split_folder = filename[0].split("/")
        print(filename)
        # folder = split_folder[len(split_folder) - 1]
        if (split_filename[5] == "default" or split_filename[7] == "default"): 
            cpu = split_filename[5]
            gpu = split_filename[7]
        else:
            cpu = int(split_filename[5])
            gpu = int(split_filename[7])

        return [cpu, gpu]

    def parse_file(self):
        if not os.path.exists(self.log_file):
            print('Path to log file is invalid\n')
            return

        csv_file = os.path.splitext(self.log_file)[0] + '.csv'
        summary = 'summary.csv'

        with open(csv_file, 'w', newline='') as fopen:
            writer = csv.writer(fopen)

            with open(self.log_file, 'r') as log:
                data = log.readlines()
                labels = self.create_header(data[0], self.log_file)
                writer.writerow(labels)
                time = 0
                number = 0
                cpu_f = 0
                cpu_0 = 0
                cpu_3 = 0
                cpu_4 = 0
                cpu_5 = 0
                cpu_max = 0
                used_gr3d = 0
                gr3d_f = 0
                cpu_p = 0
                gpu_p = 0
                ddr_p = 0
                total_p = 0
                for i, line in enumerate(data[0:]):
                    row_data = list(self.parse_data(line, self.log_file).values())
                    row = [i, time] + row_data
                    writer.writerow(row)
                    time = time + self.interval
                    cpu_f = cpu_f + int(row_data[0])
                    cpu_0 = cpu_0 + int(row_data[1])
                    cpu_3 = cpu_3 + int(row_data[2])
                    cpu_4 = cpu_4 + int(row_data[3])
                    cpu_5 = cpu_5 + int(row_data[4])
                    cpu_max = cpu_max + int(row_data[5])
                    used_gr3d = used_gr3d + int(row_data[6])
                    gr3d_f = gr3d_f + int(row_data[7])
                    cpu_p = cpu_p + int(row_data[8])
                    gpu_p = gpu_p + int(row_data[9])
                    ddr_p = ddr_p + int(row_data[10])
                    total_p = total_p + int(row_data[11])
                    number = number + 1
                total_time = (time - self.interval)

        with open(summary, 'a', newline='') as fopen:
            writer = csv.writer(fopen)
            record = []
            index = self.parse_filename(csv_file)
            for i in index:
                record.append(i)
            record.append(int(total_time))
            #record.append(0)
            record.append(int(cpu_f/number))
            record.append(int(gr3d_f/number))
            record.append(int(cpu_max/number))
            record.append(int(used_gr3d/number))
            cpu_power = int(cpu_p/number)
            gpu_power = int(gpu_p/number)
            ddr_power = int(ddr_p/number)
            record.append(cpu_power)
            record.append(gpu_power)
            record.append(ddr_power)
            record.append(cpu_power + gpu_power + ddr_power)
            record.append(int(total_p/number))
            edp = round(((cpu_power + gpu_power + ddr_power) * int(total_time) * int(total_time))/1000000000, 3)
            record.append(edp)
            #record.append(0)
            writer.writerow(record)
        return csv_file

if __name__ == '__main__':
    interval = 1000
    log_file = 'output.txt'
    parser = Parse(0, log_file)
    parser = Parse(interval, log_file)
    parser.parse_file()
