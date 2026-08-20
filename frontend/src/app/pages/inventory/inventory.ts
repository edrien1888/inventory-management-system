import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-inventory',
  imports: [CommonModule],
  templateUrl: './inventory.html',
  styleUrl: './inventory.css'
})
export class Inventory implements OnInit {
  movements = signal<any[]>([]);
  errorMessage = signal('');

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.loadMovements();
  }

  loadMovements() {
    const token = localStorage.getItem('access_token');

    if (!token) {
      this.errorMessage.set('No hay una sesión iniciada');
      return;
    }

    this.http.get<any[]>(
      'http://127.0.0.1:8000/movements',
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    ).subscribe({
      next: (data) => {
        console.log('Movimientos recibidos:', data);
        this.movements.set(data);
      },

      error: (error) => {
        console.error('Error cargando movimientos:', error);

        if (error.status === 401) {
          this.errorMessage.set(
            'Tu sesión expiró. Vuelve a iniciar sesión.'
          );
        } else {
          this.errorMessage.set(
            'No se pudieron cargar los movimientos'
          );
        }
      }
    });
  }
}