/*
  Warnings:

  - Added the required column `category` to the `RssEntries` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "RssEntries" ADD COLUMN     "category" TEXT NOT NULL;
