import { Routes } from '@angular/router';

import { Categories } from './pages/categories/categories';
import { Dashboard } from './pages/dashboard/dashboard';
import { Inventory } from './pages/inventory/inventory';
import { Login } from './pages/login/login';
import { Products } from './pages/products/products';

export const routes: Routes = [
                {
                                path: '',
                                redirectTo: 'login',
                                pathMatch: 'full'
                },
                {
                                path: 'login',
                                component: Login
                },
                {
                                path: 'dashboard',
                                component: Dashboard
                },
                {
                                path: 'categories',
                                component: Categories
                },
                {
                                path: 'products',
                                component: Products
                },
                {
                                path: 'inventory',
                                component: Inventory
                }
];