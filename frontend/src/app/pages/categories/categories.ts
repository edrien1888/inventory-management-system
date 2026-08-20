import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-categories',
  imports: [CommonModule],
  templateUrl: './categories.html',
  styleUrl: './categories.css'
})
export class Categories implements OnInit {
  categories = signal<any[]>([]);
  errorMessage = signal('');

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.loadCategories();
  }

  loadCategories() {
    const token = localStorage.getItem('access_token');

    if (!token) {
      this.errorMessage.set('No hay una sesión iniciada');
      return;
    }

    this.http.get<any[]>(
      'https://inventory-management-api-hdxr.onrender.com/categories',
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    ).subscribe({
      next: (data) => {
        console.log('Categorías recibidas:', data);
        this.categories.set(data);
      },

      error: (error) => {
        console.error('Error cargando categorías:', error);
        this.errorMessage.set(
          'No se pudieron cargar las categorías'
        );
      }
    });
  }
}