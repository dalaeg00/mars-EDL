# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 10:26:47 2021

@author: Dani
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pylab as pl
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter 

# =============================================================================
# Funciones básicas
# =============================================================================
def integra(y, q1, h):
    y_siguiente = y+q1*h
    return y_siguiente

# =============================================================================
# Modelo atmosférico simplificado
# =============================================================================

# Temperatura: Ajuste polinómico de mediciones de sonda Viking 1.
#   Altitud en km, Temperatura en K
df=pd.read_csv('viking1.csv', sep=';',header=None,decimal=',')
df[0].values

# Propiedades del gas en Marte
R_gas = 188.92
gamma_gas = 1.2941

plt.style.use('default')
plt.plot(df[1],df[0])
z = np.polyfit(df[1][:], df[0][:], 7)
temperature = np.poly1d(z)
xp_linear = np.linspace(0, 120, 100)
plt.plot(df[1], df[0], '.', label='Mediciones Viking 1')
plt.plot(xp_linear, temperature(xp_linear), '-', label='Modelo simulado')
plt.plot(xp_linear, -23.4+273.15 - 0.00222*1000*xp_linear, label='Modelo NASA Zona 1')
plt.plot(xp_linear, -31+273.15 - 0.000998*1000*xp_linear, label='Modelo NASA Zona 2')
plt.legend(loc="lower left")
plt.xlabel("Altitud (km)")
plt.ylabel("Temperatura (K)")
plt.title("Modelos de perfiles de temperatura en la atmósfera de Marte")

# Presión: 
def presion_marte(z):
    h = z*1000 # metros
    # Presión del aire a partir de la altura en km
    p = .699 * np.exp(-0.00009*h)*1000 #Pa
    return p

# Densidad:
def rho(z):
    r = presion_marte(z)/(R_gas*temperature(z))
    return r

# Plots
fig = plt.figure(figsize=(20,10))
# Plot de T
ax = fig.add_subplot(131)
ax.set_xlabel('Altitud (km)')
ax.set_ylabel('Temperatura (K)')
ax.plot(xp_linear, temperature(xp_linear), 'gs-')
ax.set_title('Temperatura en función de la altitud')

# Plot de P
ax = fig.add_subplot(132)
ax.set_xlabel('Altitud (km)')
ax.set_ylabel('Presión (Pa)')
ax.plot(xp_linear, presion_marte(xp_linear), 'cs-')
ax.set_title('Presión en función de la altitud')

# Plot de rho
ax2 = fig.add_subplot(133)
ax2.set_xlabel('Altitud (km)')
ax2.set_ylabel('Densidad (kg/m^3)')
ax2.set_title('Densidad en función de la altitud')
ax2.plot(xp_linear, rho(xp_linear), 'rs-')
plt.show()


# =============================================================================
# Simulación del amartizaje
# =============================================================================

# Constantes del problema
g = 3.721  # m/s^2

# Parámetros de configuración
h0 =30000 # metros
h1 =12400 # metros
h2 = 1500 # metros
s0 = 8 # m^2. pi*3**2/4
s1 = 0 # m^2 Al final medirá 21.5**2*pi/4 = 363 m^2
m = 1293 # kg
mf = 1255.63 # kg
t0 = 0 # segundos
t_elapsed = 0 #segundos
t_combustion = 154 #segundos
v0 = -800 # m/s
dt = 0.1 # segundos
Cd0 = 1.3
Cd1 = 0.39
v_e = 200 # m/s

def vel_sonido(h):
    velocidad_sonido = np.sqrt(gamma_gas*R_gas*temperature(h/1000))
    return velocidad_sonido

def Mach(velocidad,h):
    mach_number = abs(velocidad)/vel_sonido(h)
    return mach_number

def factor_compresibilidad(mach):
    if mach <= 0.7:
        factor = 1/(np.sqrt(1-(mach**2)))
    elif 0.7 < mach <= 1:
        factor = 1/(np.sqrt(1-(0.7**2)))
    elif 1 < mach <= 1.3:
        factor = 1/(np.sqrt((1.3**2)-1))
    else:
        factor = 1/(np.sqrt((mach**2)-1))
    return factor

#Definimos el vector de condiciones iniciales
u = np.array([[t0,h0,v0, vel_sonido(h0), Mach(v0,h0), factor_compresibilidad(Mach(v0,h0))]])

# =============================================================================
# Plot de la simulación del amartizaje
# =============================================================================
"""
fig = plt.figure(figsize=(16,16))
axis = plt.axes(xlim =(0, 100), ylim =(0, 30000)) 
line, = axis.plot(u[0,0], u[0,1], lw = 2)

fig2 = plt.figure(figsize=(16,16))
axis2 = plt.axes(xlim =(0, 100), ylim =(0, 1000)) 
line2, = axis2.plot(u[0,0], -u[0,2], lw = 2)

"""

# Plot de la altura en función del tiempo
plt.rcParams.update({'font.size': 16})
plt.style.use('dark_background')
fig = plt.figure(figsize=(16,16))
ax = fig.add_subplot(211)
ax.set_xlabel('Tiempo (s)')
ax.set_ylabel('Altura (m)')
ax.set_title('Altura de la nave en función del tiempo')
ax.set_xlim([0, 160])
ax.set_ylim([0,36000]) 
time_text = ax.text(120, 32000,'', fontsize=18)
height_text = ax.text(120, 29000,'', fontsize=18)
speed_text = ax.text(120, 26000,'', fontsize=18)
mach_text = ax.text(120, 23000,'', fontsize=18)
line, = ax.plot(u[:,0], u[:,1], 'y-', lw=3,)

# Plot de la velocidad en función del tiempo
ax2 = fig.add_subplot(212)
ax2.set_xlabel('Tiempo (s)')
ax2.set_ylabel('Velocidad (m/s)')
ax2.set_title('Velocidad de la nave en función del tiempo')
ax2.set_xlim([0, 160])
ax2.set_ylim([0,1000])
line2, = ax2.plot(u[:,0], -u[:,2], lw=3)  

# Bucle para calcular el resto de altitudes 
i = 0
while u[i,1]>0:
    if u[i,1]>=h1: # Condición que determina si el paracaídas se ha abierto ya o no.
        s = s0
        fuerza = 0.5*rho(u[i,1]/1000)*s0*Cd0*u[i,5]*u[i,2]**2
        s1 = 0
        a_cohete = 0
    elif h2 < u[i,1] < h1:
        if s1 < 330:
            s1 += 10
            print(s1)
        fuerza = 0.5*rho(u[i,1]/1000)*s0*Cd0*u[i,2]**2 + 0.5*rho(u[i,1]/1000)*s1*Cd1*u[i,5]*u[i,2]**2
        a_cohete = 0
    else:
        fuerza = 0.5*rho(u[i,1]/1000)*s0*Cd0*u[i,5]*u[i,2]**2
        a_cohete = v_e*np.log((m-((m-mf)*t_elapsed/t_combustion))/mf)
        t_elapsed += 0.1 #segundos
        if t_elapsed >= t_combustion:
            t_elapsed = t_combustion
        print(a_cohete, t_elapsed)
    f = np.array([0, u[i,2], (fuerza/m)-g+a_cohete, 0, 0, 0])
    u = np.vstack([u, integra(u[i,:],f,dt)])
    u[i+1,0] = u[i,0]+dt # Cálculo del tiempo total
    u[i+1,3] = vel_sonido(u[i,1]) # Cálculo de la velocidad del sonido
    u[i+1,4] = Mach(u[i,2],u[i,1]) # Cálculo del Mach
    u[i+1,5] = factor_compresibilidad(u[i+1,4]) # Cálculo del factor de compresibilidad
    
    i += 1
    
i_final = i

def animate(i): 
    time_text.set_text('Tiempo: ' + str(round(u[i,0],1)) + "s")
    height_text.set_text('Altitud: ' + str(round(u[i,1],1)) + "m")
    speed_text.set_text('Velocidad: ' + str(round(-u[i,2],1)) + "m/s")
    mach_text.set_text('Mach: ' + str(round(u[i,4],1)))
    line.set_data(u[:i,0], u[:i,1]) 
    line2.set_data(u[:i,0], -u[:i,2]) 
    return (line, line2, time_text, height_text, speed_text, mach_text)


def init(): 
    time_text.set_text('Tiempo: ' + str(round(u[0,0],1)) + "s")
    height_text.set_text('Altitud: ' + str(round(u[0,1],1)) + "m")
    speed_text.set_text('Altitud: ' + str(round(-u[0,2],1)) + "m/s")
    mach_text.set_text('Mach: ' + str(round(u[0,4],1)))
    line.set_data([], []) 
    line2.set_data([], []) 
    return (line, line2, time_text, height_text, speed_text, mach_text)


anim = animation.FuncAnimation(fig, animate, init_func = init, 
                               frames = int(len(u[:,0])/1), interval = 10,  blit = True) 
writer = PillowWriter(fps=10)  
anim.save("descenso.gif", writer=writer) 

# ----------------------------------

# Plot de todo en uno
# Plot de la altura en función del tiempo
plt.rcParams.update({'font.size': 15})
plt.style.use('dark_background')
fig = plt.figure(figsize=(16,132))
ax = fig.add_subplot(211)
ax.set_xlabel('Tiempo (s)')
ax.set_ylabel('Altura (m)')
ax.set_title('Altura de la nave en función del tiempo')
ax.set_xlim([0, 160])
ax.set_ylim([0,36000]) 
line, = ax.plot(u[:,0], u[:,1], 'r-', lw=3,)

# Plot de la velocidad en función del tiempo
ax2 = fig.add_subplot(212)
ax2.set_xlabel('Tiempo (s)')
ax2.set_ylabel('Velocidad (m/s)')
ax2.set_title('Velocidad de la nave en función del tiempo')
ax2.set_xlim([0, 160])
ax2.set_ylim([0,1000])
line2, = ax2.plot(u[:,0], -u[:,2], lw=3) 

# -----------------------------------

# Plot de la velocidad del sonido
plt.rcParams.update({'font.size': 15})
plt.style.use('dark_background')
fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(131)
ax.set_xlabel('Tiempo (s)')
ax.set_ylabel('Vel. del sonido (m/s)')
ax.set_title('Vel. sonido en función del tiempo')
ax.set_xlim([0, 160])
ax.set_ylim([000,260]) 
line, = ax.plot(u[:,0], u[:,3], 'r-', lw=3,)

# Plot del Mach
ax2 = fig.add_subplot(132)
ax2.set_xlabel('Tiempo (s)')
ax2.set_ylabel('Mach')
ax2.set_title('Mach de la nave en función del tiempo')
ax2.set_xlim([0, 160])
ax2.set_ylim([0,4])
line2, = ax2.plot(u[:,0], u[:,4], lw=3) 

# Plot del factor de compresibilidad
ax3 = fig.add_subplot(133)
ax3.set_xlabel('Tiempo (s)')
ax3.set_ylabel('Factor de compresibilidad')
ax3.set_title('F. de compresibilidad en función del tiempo')
ax3.set_xlim([0, 160])
ax3.set_ylim([0,2])
line3, = ax3.plot(u[:,0], u[:,5], 'g-', lw=3) 