import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-products',
  imports: [CommonModule],
  templateUrl: './products.html',
  styleUrl: './products.css'
})
export class Products implements OnInit {
  products = signal<any[]>([]);
  errorMessage = signal('');

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.loadProducts();
  }

  loadProducts() {
    const token = localStorage.getItem('access_token');

    if (!token) {
      this.errorMessage.set('No hay una sesión iniciada');
      return;
    }

    this.http.get<any[]>(
      'http://127.0.0.1:8000/products',
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    ).subscribe({
      next: (data) => {
        console.log('Productos recibidos:', data);
        this.products.set(data);
      },

      error: (error) => {
        console.error('Error cargando productos:', error);
        this.errorMessage.set(
          'No se pudieron cargar los productos'
        );
      }
    });
  }
}
